import unittest
import uuid
from datetime import UTC, datetime

from events.envelope import EventEnvelope
from outbox.postgres_store import PostgresOutboxStore
from outbox.service import dispatch_pending

from _postgres import connect


class _FailingTransport:
    def deliver(self, envelope):
        raise ConnectionError("simulated destination failure")


class _RecordingTransport:
    def __init__(self):
        self.delivered = []

    def deliver(self, envelope):
        self.delivered.append(envelope)


class PostgresOutboxStoreTests(unittest.TestCase):
    def setUp(self):
        self.connection = connect()
        self.event_id = str(uuid.uuid4())
        self.tenant_id = f"test-tenant-{uuid.uuid4()}"
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM baobab.event_outbox WHERE event_id = %s::uuid", (self.event_id,))
        self.connection.commit()
        self.connection.close()

    def _envelope(self) -> EventEnvelope:
        return EventEnvelope(
            event_id=self.event_id,
            event_type="erp.payment.completed.v1",
            schema_version="1.0",
            occurred_at=datetime.now(UTC),
            source="baobab-erp",
            correlation_id="cor-1",
            tenant_id=self.tenant_id,
            entity_id="THAMANI-GLOBAL",
            payload={"amount": 42},
        )

    def test_record_then_dispatch_delivers_and_marks_delivered(self):
        store = PostgresOutboxStore(self.connection)
        store.record(self._envelope())
        self.connection.commit()

        transport = _RecordingTransport()
        dispatch_pending(store, transport)

        self.assertEqual(len(transport.delivered), 1)
        self.assertEqual(transport.delivered[0].payload, {"amount": 42})

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT status FROM baobab.event_outbox WHERE event_id = %s::uuid", (self.event_id,)
            )
            (status,) = cursor.fetchone()
        self.assertEqual(status, "delivered")

    def test_failed_delivery_increments_attempts_and_retries(self):
        store = PostgresOutboxStore(self.connection)
        store.record(self._envelope())
        self.connection.commit()

        dispatch_pending(store, _FailingTransport())

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT status, attempts, last_error FROM baobab.event_outbox WHERE event_id = %s::uuid",
                (self.event_id,),
            )
            status, attempts, last_error = cursor.fetchone()
        self.assertEqual(status, "retry")
        self.assertEqual(attempts, 1)
        self.assertIn("simulated destination failure", last_error)


if __name__ == "__main__":
    unittest.main()
