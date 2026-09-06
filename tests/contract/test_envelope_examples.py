"""Every example under contracts/events/examples/ must satisfy both the JSON Schema
envelope and the EventEnvelope parser modules/erp code actually runs against."""

import json
import re
import unittest
from pathlib import Path

from events.envelope import EventEnvelope

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "contracts/events/envelope.schema.json"
EXAMPLES_DIR = REPO_ROOT / "contracts/events/examples"


class EnvelopeExampleTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text())
        self.examples = sorted(EXAMPLES_DIR.glob("*.json"))
        self.assertTrue(self.examples, "expected at least one example event")

    def test_examples_parse_as_event_envelopes(self):
        for example_path in self.examples:
            with self.subTest(example=example_path.name):
                value = json.loads(example_path.read_text())
                EventEnvelope.from_dict(value)

    def test_examples_satisfy_required_fields_and_event_type_pattern(self):
        required = set(self.schema["required"])
        pattern = re.compile(self.schema["properties"]["event_type"]["pattern"])
        for example_path in self.examples:
            with self.subTest(example=example_path.name):
                value = json.loads(example_path.read_text())
                missing = required - value.keys()
                self.assertFalse(missing, f"{example_path.name} missing {missing}")
                self.assertRegex(value["event_type"], pattern)
                self.assertIn(value["source"], self.schema["properties"]["source"]["enum"])


if __name__ == "__main__":
    unittest.main()
