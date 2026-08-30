import importlib.util
import unittest
from datetime import UTC
from pathlib import Path


MODULE = Path(__file__).parents[1] / "apps/baobab_erp/baobab_erp/integrations/envelope.py"
spec = importlib.util.spec_from_file_location("envelope", MODULE)
envelope_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(envelope_module)
EventEnvelope = envelope_module.EventEnvelope


class EventEnvelopeTests(unittest.TestCase):
    def valid_event(self):
        return {
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

    def test_parses_timezone_aware_timestamp(self):
        event = EventEnvelope.from_dict(self.valid_event())
        self.assertEqual(event.occurred_at.tzinfo, UTC)

    def test_rejects_missing_context(self):
        value = self.valid_event()
        del value["tenant_id"]
        with self.assertRaisesRegex(ValueError, "tenant_id"):
            EventEnvelope.from_dict(value)

    def test_rejects_naive_timestamp(self):
        value = self.valid_event()
        value["occurred_at"] = "2026-08-30T12:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            EventEnvelope.from_dict(value)


if __name__ == "__main__":
    unittest.main()
