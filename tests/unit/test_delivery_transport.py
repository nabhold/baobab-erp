import json
import re
import unittest
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from events.envelope import EventEnvelope
from integration.delivery_transport import WebhookDeliveryError, WebhookDestination, deliver

ISO_DATE_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")


def _envelope() -> EventEnvelope:
    return EventEnvelope(
        event_id="evt-1",
        event_type="erp.payment.completed.v1",
        schema_version="1.0",
        occurred_at=datetime.now(UTC),
        source="baobab-erp",
        correlation_id="cor-1",
        tenant_id="tenant-1",
        entity_id="THAMANI-GLOBAL",
        payload={"amount": 100},
    )


class _RecordingHandler(BaseHTTPRequestHandler):
    received_bodies: list[bytes] = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        self.__class__.received_bodies.append(self.rfile.read(length))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


class DeliveryTransportTests(unittest.TestCase):
    def setUp(self):
        _RecordingHandler.received_bodies = []
        self.server = HTTPServer(("127.0.0.1", 0), _RecordingHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.server.server_close)

    def _destination(self) -> WebhookDestination:
        port = self.server.server_address[1]
        return WebhookDestination(url=f"http://127.0.0.1:{port}/webhook", signing_secret="secret")

    def test_occurred_at_is_rfc3339_on_the_wire(self):
        deliver(_envelope(), self._destination())
        body = json.loads(_RecordingHandler.received_bodies[0])
        self.assertRegex(body["occurred_at"], ISO_DATE_TIME)

    def test_wire_body_round_trips_through_event_envelope(self):
        deliver(_envelope(), self._destination())
        body = json.loads(_RecordingHandler.received_bodies[0])
        EventEnvelope.from_dict(body)  # must not raise

    def test_non_2xx_response_raises(self):
        class FailingHandler(_RecordingHandler):
            def do_POST(self):
                self.send_response(500)
                self.end_headers()

        self.server.RequestHandlerClass = FailingHandler
        with self.assertRaises(WebhookDeliveryError):
            deliver(_envelope(), self._destination())


if __name__ == "__main__":
    unittest.main()
