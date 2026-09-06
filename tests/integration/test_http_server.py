import hashlib
import hmac
import json
import os
import unittest
import urllib.error
import urllib.request
import uuid
from http.server import ThreadingHTTPServer
from threading import Thread

from _postgres import require_database_url

SECRET = "integration-test-secret"


class HttpServerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database_url = require_database_url()  # skips the whole class if unset
        os.environ["DATABASE_URL"] = database_url
        os.environ["BAOBAB_EVENT_SIGNING_SECRET"] = SECRET

        from application.server import Config, make_handler

        config = Config()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(config))
        cls.port = cls.server.server_address[1]
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _get(self, path: str):
        request = urllib.request.Request(self._url(path))
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def _post_event(self, body: bytes, signature: str):
        request = urllib.request.Request(
            self._url("/events/inbound"), data=body, method="POST", headers={"X-Baobab-Signature": signature}
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_liveness(self):
        status, body = self._get("/health/live")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_readiness_against_real_database(self):
        status, body = self._get("/health/ready")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ready")

    def test_unknown_path_is_404(self):
        status, _ = self._get("/nope")
        self.assertEqual(status, 404)

    def test_inbound_event_end_to_end(self):
        event_id = str(uuid.uuid4())
        payload = {
            "event_id": event_id,
            "event_type": "trade.order.accepted",
            "schema_version": "1.0",
            "occurred_at": "2026-09-06T12:00:00Z",
            "source": "baobab-trade",
            "correlation_id": "cor-1",
            "tenant_id": "tenant-1",
            "entity_id": "THAMANI-GLOBAL",
            "payload": {},
        }
        body = json.dumps(payload).encode()
        signature = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
        try:
            status, response_body = self._post_event(body, signature)
            self.assertEqual(status, 200)
            self.assertEqual(response_body["event_id"], event_id)

            # duplicate delivery is accepted, not reprocessed
            status, response_body = self._post_event(body, signature)
            self.assertEqual(status, 200)
        finally:
            import psycopg

            with psycopg.connect(os.environ["DATABASE_URL"]) as connection, connection.cursor() as cursor:
                cursor.execute("DELETE FROM baobab.event_inbox WHERE event_id = %s::uuid", (event_id,))
                connection.commit()

    def test_invalid_signature_is_rejected(self):
        body = json.dumps({"event_id": "whatever"}).encode()
        status, body_json = self._post_event(body, "sha256=wrong")
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
