import hashlib
import hmac
import unittest

from security.signing import sign_body, verify_signature


class SigningTests(unittest.TestCase):
    def test_accepts_valid_sha256_signature(self):
        body = b'{"event_id":"evt-1"}'
        digest = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(verify_signature(body, f"sha256={digest}", "secret"))

    def test_rejects_wrong_signature(self):
        self.assertFalse(verify_signature(b"body", "sha256=wrong", "secret"))

    def test_rejects_missing_secret(self):
        self.assertFalse(verify_signature(b"body", "sha256=value", ""))

    def test_sign_body_round_trips_with_verify(self):
        body = b'{"event_id":"evt-2"}'
        signature = sign_body(body, "secret")
        self.assertTrue(verify_signature(body, signature, "secret"))

    def test_sign_body_wrong_secret_fails_verification(self):
        body = b'{"event_id":"evt-2"}'
        signature = sign_body(body, "secret")
        self.assertFalse(verify_signature(body, signature, "different-secret"))


if __name__ == "__main__":
    unittest.main()
