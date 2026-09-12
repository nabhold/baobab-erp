import time
import unittest

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from security.workload_auth import TokenValidationError, verify_workload_token

ISSUER = "https://iam.example.invalid/realms/baobab"
AUDIENCE = "baobab-erp"


class FixedKeyResolver:
    """A SigningKeyResolver returning a fixed key, standing in for a real JWKS fetch."""

    def __init__(self, key):
        self._key = key

    def resolve(self, token: str):
        return self._key


class WorkloadAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_key = cls.private_key.public_key()

    def _token(self, **overrides) -> str:
        now = int(time.time())
        claims = {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "service-account-baobab-erp-workload",
            "azp": "baobab-erp-workload",
            "actor_type": "workload",
            "scope": "erp:integrate",
            "iat": now,
            "exp": now + 300,
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    def _verify(self, token: str):
        return verify_workload_token(
            f"Bearer {token}",
            issuer=ISSUER,
            audience=AUDIENCE,
            key_resolver=FixedKeyResolver(self.public_key),
        )

    def test_accepts_a_valid_workload_token(self):
        identity = self._verify(self._token())
        self.assertEqual(identity.principal, "baobab-erp-workload")
        self.assertTrue(identity.has_role("erp:integrate"))

    def test_falls_back_to_sub_when_azp_absent(self):
        identity = self._verify(self._token(azp=None))
        self.assertEqual(identity.principal, "service-account-baobab-erp-workload")

    def test_rejects_missing_authorization_header(self):
        with self.assertRaises(TokenValidationError):
            verify_workload_token(
                None, issuer=ISSUER, audience=AUDIENCE, key_resolver=FixedKeyResolver(self.public_key)
            )

    def test_rejects_non_bearer_scheme(self):
        with self.assertRaises(TokenValidationError):
            verify_workload_token(
                "Basic dXNlcjpwYXNz",
                issuer=ISSUER,
                audience=AUDIENCE,
                key_resolver=FixedKeyResolver(self.public_key),
            )

    def test_rejects_wrong_issuer(self):
        token = self._token(iss="https://not-baobab-iam.example.invalid/realms/other")
        with self.assertRaises(TokenValidationError):
            self._verify(token)

    def test_rejects_wrong_audience(self):
        token = self._token(aud="baobab-control-plane")
        with self.assertRaises(TokenValidationError):
            self._verify(token)

    def test_rejects_expired_token(self):
        now = int(time.time())
        token = self._token(iat=now - 3600, exp=now - 1800)
        with self.assertRaises(TokenValidationError):
            self._verify(token)

    def test_rejects_non_workload_actor_type(self):
        token = self._token(actor_type="human")
        with self.assertRaises(TokenValidationError):
            self._verify(token)

    def test_rejects_signature_from_a_different_key(self):
        other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        now = int(time.time())
        token = jwt.encode(
            {
                "iss": ISSUER,
                "aud": AUDIENCE,
                "sub": "sub",
                "azp": "baobab-erp-workload",
                "actor_type": "workload",
                "iat": now,
                "exp": now + 300,
            },
            other_key,
            algorithm="RS256",
        )
        with self.assertRaises(TokenValidationError):
            self._verify(token)

    def test_rejects_token_with_no_principal(self):
        token = self._token(azp=None, sub=None)
        with self.assertRaises(TokenValidationError):
            self._verify(token)


if __name__ == "__main__":
    unittest.main()
