import hashlib
import hmac


def sign_body(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(body: bytes, supplied_signature: str, secret: str) -> bool:
    if not body or not supplied_signature or not secret:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    normalized = supplied_signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, normalized)
