import unittest

from context.model import ContextResolutionError, TenantContext
from context.resolver import resolve_context


class FakeMappingStore:
    def __init__(self, mappings):
        self._mappings = mappings

    def find_active_mapping(self, tenant_id, entity_id):
        return self._mappings.get((tenant_id, entity_id))


class ContextResolverTests(unittest.TestCase):
    def setUp(self):
        self.store = FakeMappingStore({("nabhold", "nabhold-legal"): (1000, 1)})

    def test_resolves_active_mapping(self):
        context = resolve_context("nabhold", "nabhold-legal", self.store)
        self.assertEqual(context, TenantContext("nabhold", "nabhold-legal", 1000, 1))

    def test_missing_tenant_id_fails_closed(self):
        with self.assertRaises(ContextResolutionError):
            resolve_context(None, "nabhold-legal", self.store)

    def test_missing_entity_id_fails_closed(self):
        with self.assertRaises(ContextResolutionError):
            resolve_context("nabhold", None, self.store)

    def test_unmapped_pair_fails_closed(self):
        with self.assertRaises(ContextResolutionError):
            resolve_context("nabhold", "unknown-legal-entity", self.store)

    def test_cross_tenant_pair_fails_closed(self):
        """NABHOLD -> THAMANI must never resolve: distinct tenants stay isolated."""
        with self.assertRaises(ContextResolutionError):
            resolve_context("thamani", "nabhold-legal", self.store)


if __name__ == "__main__":
    unittest.main()
