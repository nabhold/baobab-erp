import unittest

from mapping.model import MappingNotFoundError, NativeRecordRef
from mapping.resolver import resolve_to_canonical, resolve_to_native


class FakeStore:
    def __init__(self):
        self._native = {}
        self._canonical = {}

    def add(self, tenant_id, canonical_type, canonical_id, table, record_id):
        self._native[(tenant_id, canonical_type, canonical_id)] = NativeRecordRef(table, record_id)
        self._canonical[(tenant_id, table, record_id)] = canonical_id

    def find_native(self, tenant_id, canonical_type, canonical_id):
        return self._native.get((tenant_id, canonical_type, canonical_id))

    def find_canonical(self, tenant_id, table, record_id):
        return self._canonical.get((tenant_id, table, record_id))


class MappingResolverTests(unittest.TestCase):
    def setUp(self):
        self.store = FakeStore()
        self.store.add("tenant-1", "Party", "canon-1", "C_BPartner", 1001)

    def test_resolves_to_native(self):
        ref = resolve_to_native("tenant-1", "Party", "canon-1", self.store)
        self.assertEqual(ref, NativeRecordRef("C_BPartner", 1001))

    def test_resolves_to_canonical(self):
        canonical_id = resolve_to_canonical("tenant-1", "C_BPartner", 1001, self.store)
        self.assertEqual(canonical_id, "canon-1")

    def test_missing_native_mapping_raises(self):
        with self.assertRaises(MappingNotFoundError):
            resolve_to_native("tenant-1", "Party", "unknown", self.store)

    def test_cross_tenant_lookup_fails_closed(self):
        with self.assertRaises(MappingNotFoundError):
            resolve_to_native("tenant-2", "Party", "canon-1", self.store)


if __name__ == "__main__":
    unittest.main()
