from typing import Protocol

from mapping.model import MappingNotFoundError, NativeRecordRef


class CanonicalMappingStore(Protocol):
    """Backing store for CanonicalEntity <-> iDempiere native record mappings."""

    def find_native(self, tenant_id: str, canonical_type: str, canonical_id: str) -> NativeRecordRef | None: ...

    def find_canonical(self, tenant_id: str, table: str, record_id: int) -> str | None: ...


def resolve_to_native(
    tenant_id: str,
    canonical_type: str,
    canonical_id: str,
    store: CanonicalMappingStore,
) -> NativeRecordRef:
    ref = store.find_native(tenant_id, canonical_type, canonical_id)
    if ref is None:
        raise MappingNotFoundError(
            f"No active mapping for tenant_id={tenant_id!r} canonical_type={canonical_type!r} "
            f"canonical_id={canonical_id!r}"
        )
    return ref


def resolve_to_canonical(
    tenant_id: str,
    table: str,
    record_id: int,
    store: CanonicalMappingStore,
) -> str:
    canonical_id = store.find_canonical(tenant_id, table, record_id)
    if canonical_id is None:
        raise MappingNotFoundError(
            f"No active mapping for tenant_id={tenant_id!r} table={table!r} record_id={record_id!r}"
        )
    return canonical_id
