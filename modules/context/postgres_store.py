"""Postgres-backed TenantMappingStore against baobab.tenant_mapping.

See db/migrations/0002_create_tenant_mapping.sql for the schema and
db/migrations/0006_add_tenant_mapping_native_unique_index.sql for the unique index
that makes find_by_native unambiguous. This class holds no connection of its own; the
caller passes a live psycopg connection so context resolution participates in
whatever transaction (if any) the caller is already in.
"""

import psycopg


class PostgresTenantMappingStore:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def find_active_mapping(self, tenant_id: str, entity_id: str) -> tuple[int, int] | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ad_client_id, ad_org_id
                FROM baobab.tenant_mapping
                WHERE tenant_id = %s AND entity_id = %s AND status = 'active'
                """,
                (tenant_id, entity_id),
            )
            row = cursor.fetchone()
        return (row[0], row[1]) if row else None

    def find_by_native(self, ad_client_id: int, ad_org_id: int) -> tuple[str, str] | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tenant_id, entity_id
                FROM baobab.tenant_mapping
                WHERE ad_client_id = %s AND ad_org_id = %s AND status = 'active'
                """,
                (ad_client_id, ad_org_id),
            )
            row = cursor.fetchone()
        return (row[0], row[1]) if row else None
