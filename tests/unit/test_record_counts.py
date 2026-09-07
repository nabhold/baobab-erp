import unittest

from reconciliation.record_counts import reconcile_record_counts


class FakeCountable:
    def __init__(self, counts):
        self._counts = counts

    def count(self, tenant_id, category):
        return self._counts[(tenant_id, category)]


class RecordCountsReconciliationTests(unittest.TestCase):
    def test_matching_counts_reconcile(self):
        left = FakeCountable({("nabhold", "orders"): 1042})
        right = FakeCountable({("nabhold", "orders"): 1042})

        result = reconcile_record_counts("nabhold", "orders", left, right)

        self.assertTrue(result.matches)
        self.assertEqual((result.left_count, result.right_count), (1042, 1042))

    def test_mismatched_counts_do_not_reconcile(self):
        left = FakeCountable({("nabhold", "orders"): 1042})
        right = FakeCountable({("nabhold", "orders"): 1040})

        result = reconcile_record_counts("nabhold", "orders", left, right)

        self.assertFalse(result.matches)
        self.assertEqual((result.left_count, result.right_count), (1042, 1040))

    def test_cross_tenant_counts_are_not_conflated(self):
        left = FakeCountable({("nabhold", "orders"): 5, ("thamani", "orders"): 9})
        right = FakeCountable({("nabhold", "orders"): 5, ("thamani", "orders"): 9})

        result = reconcile_record_counts("nabhold", "orders", left, right)

        self.assertEqual((result.left_count, result.right_count), (5, 5))


if __name__ == "__main__":
    unittest.main()
