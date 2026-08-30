import hashlib
import hmac
import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).parents[1] / "apps/baobab_erp/baobab_erp/integrations/signing.py"
spec = importlib.util.spec_from_file_location("signing", MODULE)
signing = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(signing)


class SigningTests(unittest.TestCase):
    def test_accepts_valid_sha256_signature(self):
        body = b'{"event_id":"evt-1"}'
        digest = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(signing.verify_signature(body, f"sha256={digest}", "secret"))

    def test_rejects_wrong_signature(self):
        self.assertFalse(signing.verify_signature(b"body", "sha256=wrong", "secret"))

    def test_rejects_missing_secret(self):
        self.assertFalse(signing.verify_signature(b"body", "sha256=value", ""))


if __name__ == "__main__":
    unittest.main()
