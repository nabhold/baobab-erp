from jwt import PyJWKClient


class JwksSigningKeyResolver:
    """A SigningKeyResolver backed by an OIDC issuer's real JWKS endpoint.
    PyJWKClient does its own bounded in-memory caching (`lifespan`), so a resolver
    instance is safe to reuse across every request rather than refetching the JWKS on
    each call.
    """

    def __init__(self, jwks_uri: str, cache_ttl_seconds: int = 300) -> None:
        self._client = PyJWKClient(jwks_uri, cache_keys=True, lifespan=cache_ttl_seconds)

    def resolve(self, token: str) -> str:
        return self._client.get_signing_key_from_jwt(token).key
