"""Postgres-backed CanonicalMappingStore against baobab.entity_mapping.

See db/migrations/0003_create_entity_mapping.sql. canonical_id is stored as a
native UUID column; this class accepts/returns it as str at the boundary, matching
the rest of modules/mapping, and casts explicitly in SQL rather than relying on
implicit driver-side UUID adaptation.
"""

import psycopg

from mapping.model import NativeRecordRef


class PostgresCanonicalMappingStore:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def find_native(self, tenant_id: str, canonical_type: str, canonical_id: str) -> NativeRecordRef | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT native_table, native_id
                FROM baobab.entity_mapping
                WHERE tenant_id = %s
                  AND canonical_type = %s
                  AND canonical_id = %s::uuid
                  AND status = 'active'
                """,
                (tenant_id, canonical_type, canonical_id),
            )
            row = cursor.fetchone()
        return NativeRecordRef(table=row[0], record_id=row[1]) if row else None

    def find_canonical(self, tenant_id: str, table: str, record_id: int) -> str | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT canonical_id::text
                FROM baobab.entity_mapping
                WHERE tenant_id = %s
                  AND native_table = %s
                  AND native_id = %s
                  AND status = 'active'
                """,
                (tenant_id, table, record_id),
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def active_canonical_ids(self, tenant_id: str, canonical_type: str) -> set[str]:
        """Backs identity reconciliation (ADR-ERP-011 section 64): every canonical id
        this tenant currently has an active native mapping for, regardless of which
        native record it points at.
        """
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT canonical_id::text
                FROM baobab.entity_mapping
                WHERE tenant_id = %s
                  AND canonical_type = %s
                  AND status = 'active'
                """,
                (tenant_id, canonical_type),
            )
            return {row[0] for row in cursor.fetchall()}
