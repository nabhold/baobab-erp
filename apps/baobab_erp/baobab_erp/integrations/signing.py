import hashlib
import hmac


def verify_signature(body: bytes, supplied_signature: str, secret: str) -> bool:
	if not body or not supplied_signature or not secret:
		return False
	expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
	normalized = supplied_signature.removeprefix("sha256=")
	return hmac.compare_digest(expected, normalized)
