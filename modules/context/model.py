from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TenantContext:
    """A resolved Baobab request context. Never constructed except by `resolve_context`."""

    tenant_id: str
    entity_id: str
    ad_client_id: int
    ad_org_id: int


class ContextResolutionError(Exception):
    """Raised when tenant/entity context is missing, incomplete, or unresolved.

    Resolution fails closed per ADR-ERP-010: an incomplete or unresolved context is
    always an error, never a default.
    """
