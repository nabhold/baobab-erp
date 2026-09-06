import hashlib
import hmac
import json
import unittest

from inbox.service import InvalidSignatureError, receive


class FakeInboxStore:
    def __init__(self):
        self.seen = set()
        self.recorded = []

    def exists(self, event_id):
        return event_id in self.seen

    def record_received(self, envelope, payload_json):
        self.seen.add(envelope.event_id)
        self.recorded.append((envelope.event_id, payload_json))


def _signed_body(secret="secret"):
    payload = {
        "event_id": "evt-1",
        "event_type": "trade.order.accepted",
        "schema_version": "1.0",
        "occurred_at": "2026-08-30T12:00:00Z",
        "source": "baobab-trade",
        "correlation_id": "cor-1",
        "tenant_id": "tenant-1",
        "entity_id": "THAMANI-GLOBAL",
        "payload": {},
    }
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return body, signature


class InboxServiceTests(unittest.TestCase):
    def test_records_new_event(self):
        store = FakeInboxStore()
        body, signature = _signed_body()
        receive(body, signature, "secret", store)
        self.assertEqual(len(store.recorded), 1)

    def test_duplicate_delivery_is_not_reprocessed(self):
        store = FakeInboxStore()
        body, signature = _signed_body()
        receive(body, signature, "secret", store)
        receive(body, signature, "secret", store)
        self.assertEqual(len(store.recorded), 1)

    def test_invalid_signature_is_rejected(self):
        store = FakeInboxStore()
        body, _ = _signed_body()
        with self.assertRaises(InvalidSignatureError):
            receive(body, "sha256=wrong", "secret", store)
        self.assertEqual(len(store.recorded), 0)


if __name__ == "__main__":
    unittest.main()
