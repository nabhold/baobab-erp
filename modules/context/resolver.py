from typing import Protocol

from context.model import ContextResolutionError, TenantContext


class TenantMappingStore(Protocol):
    """Backing store for active tenant/legal-entity -> AD_Client/AD_Org mappings.

    A real implementation queries the mapping schema in db/migrations; tests use an
    in-memory fake. Neither this protocol nor its callers assume tenant_id == AD_Client_ID
    (ADR-ERP-002).
    """

    def find_active_mapping(self, tenant_id: str, entity_id: str) -> tuple[int, int] | None: ...


def resolve_context(
    tenant_id: str | None,
    entity_id: str | None,
    store: TenantMappingStore,
) -> TenantContext:
    """Resolve inbound headers into a TenantContext, or raise. Never guesses."""
    if not tenant_id or not entity_id:
        raise ContextResolutionError("Both tenant_id and entity_id are required")

    mapping = store.find_active_mapping(tenant_id, entity_id)
    if mapping is None:
        raise ContextResolutionError(
            f"No active mapping for tenant_id={tenant_id!r} entity_id={entity_id!r}"
        )

    ad_client_id, ad_org_id = mapping
    return TenantContext(tenant_id=tenant_id, entity_id=entity_id, ad_client_id=ad_client_id, ad_org_id=ad_org_id)
