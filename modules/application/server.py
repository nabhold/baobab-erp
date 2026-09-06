"""Minimal HTTP application layer: liveness/readiness probes and the inbound
signed-event webhook receiver. Deliberately stdlib-only (http.server) rather than
a web framework -- no ADR has chosen one yet, and these three endpoints don't need
one. A framework choice is tracked in architecture/conformance.yaml against
ADR-ERP-005 if/when the surface grows past this.

Each request opens its own short-lived Postgres connection: psycopg connections
are not safe to share across the threads ThreadingHTTPServer uses for concurrent
requests.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg

from application.health import liveness, readiness
from inbox.postgres_store import PostgresInboxStore
from inbox.service import InvalidSignatureError, receive


class PsycopgProbe:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def ping(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT 1")


class Config:
    def __init__(self) -> None:
        self.database_url = _require_env("DATABASE_URL")
        self.event_signing_secret = _require_env("BAOBAB_EVENT_SIGNING_SECRET")
        self.port = int(os.environ.get("HTTP_PORT", "8000"))


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


def make_handler(config: Config) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
            pass  # structured logging is deployment configuration, not hard-coded here

        def _send_json(self, status: int, body: dict) -> None:
            payload = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802 - stdlib method name
            if self.path == "/health/live":
                self._send_json(200, liveness())
                return
            if self.path == "/health/ready":
                try:
                    with psycopg.connect(config.database_url) as connection:
                        self._send_json(200, readiness(PsycopgProbe(connection)))
                except Exception as exc:  # noqa: BLE001 - reported as a 503, not raised
                    self._send_json(503, {"status": "not_ready", "error": str(exc)})
                return
            self._send_json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802 - stdlib method name
            if self.path == "/events/inbound":
                self._handle_inbound_event()
                return
            self._send_json(404, {"error": "not found"})

        def _handle_inbound_event(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
            signature = self.headers.get("X-Baobab-Signature", "")
            try:
                with psycopg.connect(config.database_url) as connection:
                    store = PostgresInboxStore(connection)
                    envelope = receive(body, signature, config.event_signing_secret, store)
            except InvalidSignatureError:
                self._send_json(401, {"error": "invalid signature"})
                return
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, {"status": "accepted", "event_id": envelope.event_id})

    return Handler


def main() -> None:
    config = Config()
    server = ThreadingHTTPServer(("0.0.0.0", config.port), make_handler(config))  # noqa: S104 - container-internal bind
    server.serve_forever()


if __name__ == "__main__":
    main()
