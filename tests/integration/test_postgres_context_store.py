import unittest
import uuid

from context.model import ContextResolutionError
from context.postgres_store import PostgresTenantMappingStore
from context.resolver import resolve_context

from _postgres import connect


class PostgresContextStoreTests(unittest.TestCase):
    def setUp(self):
        self.connection = connect()
        self.tenant_id = f"test-tenant-{uuid.uuid4()}"
        self.entity_id = f"test-entity-{uuid.uuid4()}"
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM baobab.tenant_mapping WHERE tenant_id = %s", (self.tenant_id,))
        self.connection.commit()
        self.connection.close()

    def _insert_mapping(self, status="active"):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO baobab.tenant_mapping (tenant_id, entity_id, ad_client_id, ad_org_id, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (self.tenant_id, self.entity_id, 1000, 1, status),
            )
        self.connection.commit()

    def test_resolves_a_real_active_mapping(self):
        self._insert_mapping()
        store = PostgresTenantMappingStore(self.connection)
        context = resolve_context(self.tenant_id, self.entity_id, store)
        self.assertEqual((context.ad_client_id, context.ad_org_id), (1000, 1))

    def test_suspended_mapping_fails_closed(self):
        self._insert_mapping(status="suspended")
        store = PostgresTenantMappingStore(self.connection)
        with self.assertRaises(ContextResolutionError):
            resolve_context(self.tenant_id, self.entity_id, store)

    def test_unknown_pair_fails_closed(self):
        store = PostgresTenantMappingStore(self.connection)
        with self.assertRaises(ContextResolutionError):
            resolve_context(self.tenant_id, "no-such-entity", store)


if __name__ == "__main__":
    unittest.main()
