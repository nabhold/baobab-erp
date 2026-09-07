import hashlib
import hmac
import json
import unittest
import uuid

from inbox.postgres_store import PostgresInboxStore
from inbox.service import InvalidSignatureError, receive

from _postgres import connect

SECRET = "secret"


class PostgresInboxStoreTests(unittest.TestCase):
    def setUp(self):
        self.connection = connect()
        self.event_id = str(uuid.uuid4())
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM baobab.event_inbox WHERE event_id = %s::uuid", (self.event_id,))
        self.connection.commit()
        self.connection.close()

    def _signed_body(self):
        payload = {
            "event_id": self.event_id,
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
        return body, signature

    def test_receive_persists_a_real_row(self):
        store = PostgresInboxStore(self.connection)
        body, signature = self._signed_body()
        receive(body, signature, SECRET, store)

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT status FROM baobab.event_inbox WHERE event_id = %s::uuid", (self.event_id,)
            )
            (status,) = cursor.fetchone()
        self.assertEqual(status, "received")

    def test_duplicate_delivery_does_not_insert_twice(self):
        store = PostgresInboxStore(self.connection)
        body, signature = self._signed_body()
        receive(body, signature, SECRET, store)
        receive(body, signature, SECRET, store)

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM baobab.event_inbox WHERE event_id = %s::uuid", (self.event_id,)
            )
            (count,) = cursor.fetchone()
        self.assertEqual(count, 1)

    def test_invalid_signature_is_rejected_before_any_write(self):
        store = PostgresInboxStore(self.connection)
        body, _ = self._signed_body()
        with self.assertRaises(InvalidSignatureError):
            receive(body, "sha256=wrong", SECRET, store)

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM baobab.event_inbox WHERE event_id = %s::uuid", (self.event_id,)
            )
            (count,) = cursor.fetchone()
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
