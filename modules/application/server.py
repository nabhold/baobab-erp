"""Minimal HTTP application layer: liveness/readiness probes, the inbound
signed-event webhook receiver, and context/mapping resolution for the OSGi bundles
in idempiere/extensions (they run inside iDempiere's own JVM and have no direct
access to the baobab Postgres schema; this is how they reach it). Deliberately
stdlib-only (http.server) rather than a web framework -- no ADR has chosen one yet,
and this surface doesn't need one. A framework choice is tracked in
architecture/conformance.yaml against ADR-ERP-005 if/when the surface grows past
this.

Each request opens its own short-lived Postgres connection: psycopg connections
are not safe to share across the threads ThreadingHTTPServer uses for concurrent
requests.

/context/resolve and /mapping/resolve* have no authentication of their own yet --
they rely on network-level trust (only reachable from inside the deployment's own
network, e.g. the Compose network), same gap already noted for the rest of this
module against ADR-ERP-010.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import psycopg

from application.health import liveness, readiness
from context.model import ContextResolutionError
from context.postgres_store import PostgresTenantMappingStore
from context.resolver import resolve_context
from inbox.postgres_store import PostgresInboxStore
from inbox.service import InvalidSignatureError, receive
from mapping.model import MappingNotFoundError
from mapping.postgres_store import PostgresCanonicalMappingStore
from mapping.resolver import resolve_to_canonical, resolve_to_native


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
            split = urlsplit(self.path)
            query = parse_qs(split.query)

            if split.path == "/health/live":
                self._send_json(200, liveness())
                return
            if split.path == "/health/ready":
                try:
                    with psycopg.connect(config.database_url) as connection:
                        self._send_json(200, readiness(PsycopgProbe(connection)))
                except Exception as exc:  # noqa: BLE001 - reported as a 503, not raised
                    self._send_json(503, {"status": "not_ready", "error": str(exc)})
                return
            if split.path == "/context/resolve":
                self._handle_context_resolve(query)
                return
            if split.path == "/mapping/resolve":
                self._handle_mapping_resolve(query)
                return
            if split.path == "/mapping/resolve-canonical":
                self._handle_mapping_resolve_canonical(query)
                return
            self._send_json(404, {"error": "not found"})

        def _query_param(self, query: dict, name: str) -> str | None:
            values = query.get(name)
            return values[0] if values else None

        def _handle_context_resolve(self, query: dict) -> None:
            tenant_id = self._query_param(query, "tenant_id")
            entity_id = self._query_param(query, "entity_id")
            try:
                with psycopg.connect(config.database_url) as connection:
                    store = PostgresTenantMappingStore(connection)
                    context = resolve_context(tenant_id, entity_id, store)
            except ContextResolutionError as exc:
                self._send_json(404, {"error": str(exc)})
                return
            self._send_json(200, {"ad_client_id": context.ad_client_id, "ad_org_id": context.ad_org_id})

        def _handle_mapping_resolve(self, query: dict) -> None:
            tenant_id = self._query_param(query, "tenant_id")
            canonical_type = self._query_param(query, "canonical_type")
            canonical_id = self._query_param(query, "canonical_id")
            if not tenant_id or not canonical_type or not canonical_id:
                self._send_json(
                    400, {"error": "tenant_id, canonical_type and canonical_id are all required"}
                )
                return
            try:
                with psycopg.connect(config.database_url) as connection:
                    store = PostgresCanonicalMappingStore(connection)
                    ref = resolve_to_native(tenant_id, canonical_type, canonical_id, store)
            except MappingNotFoundError as exc:
                self._send_json(404, {"error": str(exc)})
                return
            self._send_json(200, {"table": ref.table, "record_id": ref.record_id})

        def _handle_mapping_resolve_canonical(self, query: dict) -> None:
            tenant_id = self._query_param(query, "tenant_id")
            table = self._query_param(query, "table")
            record_id = self._query_param(query, "record_id")
            if not tenant_id or not table or not record_id or not record_id.isdigit():
                self._send_json(
                    400, {"error": "tenant_id, table and a numeric record_id are all required"}
                )
                return
            try:
                with psycopg.connect(config.database_url) as connection:
                    store = PostgresCanonicalMappingStore(connection)
                    canonical_id = resolve_to_canonical(tenant_id, table, int(record_id), store)
            except MappingNotFoundError as exc:
                self._send_json(404, {"error": str(exc)})
                return
            self._send_json(200, {"canonical_id": canonical_id})

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
