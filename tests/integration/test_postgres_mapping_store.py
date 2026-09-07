import unittest
import uuid

from mapping.model import MappingNotFoundError, NativeRecordRef
from mapping.postgres_store import PostgresCanonicalMappingStore
from mapping.resolver import resolve_to_canonical, resolve_to_native
from reconciliation.identity import reconcile_identity

from _postgres import connect


class PostgresMappingStoreTests(unittest.TestCase):
    def setUp(self):
        self.connection = connect()
        self.tenant_id = f"test-tenant-{uuid.uuid4()}"
        self.canonical_id = str(uuid.uuid4())
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM baobab.entity_mapping WHERE tenant_id = %s", (self.tenant_id,))
        self.connection.commit()
        self.connection.close()

    def _insert_mapping(self, canonical_id=None, native_id=1001, canonical_type="Party"):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO baobab.entity_mapping
                    (tenant_id, canonical_type, canonical_id, native_table, native_id)
                VALUES (%s, %s, %s::uuid, %s, %s)
                """,
                (self.tenant_id, canonical_type, canonical_id or self.canonical_id, "C_BPartner", native_id),
            )
        self.connection.commit()

    def test_resolves_to_native_against_real_rows(self):
        self._insert_mapping()
        store = PostgresCanonicalMappingStore(self.connection)
        ref = resolve_to_native(self.tenant_id, "Party", self.canonical_id, store)
        self.assertEqual(ref, NativeRecordRef("C_BPartner", 1001))

    def test_resolves_to_canonical_against_real_rows(self):
        self._insert_mapping()
        store = PostgresCanonicalMappingStore(self.connection)
        canonical_id = resolve_to_canonical(self.tenant_id, "C_BPartner", 1001, store)
        self.assertEqual(canonical_id, self.canonical_id)

    def test_missing_mapping_raises(self):
        store = PostgresCanonicalMappingStore(self.connection)
        with self.assertRaises(MappingNotFoundError):
            resolve_to_native(self.tenant_id, "Party", str(uuid.uuid4()), store)

    def test_identity_reconciliation_against_real_rows(self):
        missing_canonical_id = str(uuid.uuid4())
        self._insert_mapping()
        store = PostgresCanonicalMappingStore(self.connection)

        result = reconcile_identity(
            self.tenant_id, "Party", {self.canonical_id, missing_canonical_id}, store
        )

        self.assertFalse(result.matches)
        self.assertEqual(result.missing, frozenset({missing_canonical_id}))
        self.assertEqual(result.unexpected, frozenset())

    def test_identity_reconciliation_flags_unexpected_mapping(self):
        self._insert_mapping()
        store = PostgresCanonicalMappingStore(self.connection)

        result = reconcile_identity(self.tenant_id, "Party", set(), store)

        self.assertFalse(result.matches)
        self.assertEqual(result.unexpected, frozenset({self.canonical_id}))


if __name__ == "__main__":
    unittest.main()
