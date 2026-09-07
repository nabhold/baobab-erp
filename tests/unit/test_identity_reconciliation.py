import unittest

from reconciliation.identity import reconcile_identity


class FakeMappedEntityStore:
    def __init__(self, mapped):
        self._mapped = mapped

    def active_canonical_ids(self, tenant_id, canonical_type):
        return self._mapped.get((tenant_id, canonical_type), set())


class IdentityReconciliationTests(unittest.TestCase):
    def test_matching_sets_reconcile(self):
        store = FakeMappedEntityStore({("nabhold", "Party"): {"a", "b"}})

        result = reconcile_identity("nabhold", "Party", {"a", "b"}, store)

        self.assertTrue(result.matches)
        self.assertEqual(result.missing, frozenset())
        self.assertEqual(result.unexpected, frozenset())

    def test_expected_but_unmapped_entity_is_missing(self):
        store = FakeMappedEntityStore({("nabhold", "Party"): {"a"}})

        result = reconcile_identity("nabhold", "Party", {"a", "b"}, store)

        self.assertFalse(result.matches)
        self.assertEqual(result.missing, frozenset({"b"}))
        self.assertEqual(result.unexpected, frozenset())

    def test_mapped_but_no_longer_expected_entity_is_unexpected(self):
        store = FakeMappedEntityStore({("nabhold", "Party"): {"a", "b"}})

        result = reconcile_identity("nabhold", "Party", {"a"}, store)

        self.assertFalse(result.matches)
        self.assertEqual(result.missing, frozenset())
        self.assertEqual(result.unexpected, frozenset({"b"}))

    def test_cross_tenant_mappings_are_not_conflated(self):
        store = FakeMappedEntityStore({
            ("nabhold", "Party"): {"a"},
            ("thamani", "Party"): {"a"},
        })

        result = reconcile_identity("nabhold", "Party", {"a"}, store)

        self.assertTrue(result.matches)


if __name__ == "__main__":
    unittest.main()
