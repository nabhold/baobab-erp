import unittest

from provisioning.lifecycle import (
    InvalidLifecycleTransitionError,
    LegalEntityLifecycleState,
    transition,
)


class ProvisioningLifecycleTests(unittest.TestCase):
    def test_happy_path(self):
        state = LegalEntityLifecycleState.REQUESTED
        state = transition(state, LegalEntityLifecycleState.ISOLATION_PROFILE_SELECTED)
        state = transition(state, LegalEntityLifecycleState.ENGINE_INSTANCE_ASSIGNED)
        state = transition(state, LegalEntityLifecycleState.ACCOUNTING_CONFIGURED)
        state = transition(state, LegalEntityLifecycleState.ACTIVE)
        self.assertEqual(state, LegalEntityLifecycleState.ACTIVE)

    def test_cannot_skip_accounting_configuration(self):
        with self.assertRaises(InvalidLifecycleTransitionError):
            transition(LegalEntityLifecycleState.REQUESTED, LegalEntityLifecycleState.ACTIVE)

    def test_decommissioned_is_terminal(self):
        with self.assertRaises(InvalidLifecycleTransitionError):
            transition(LegalEntityLifecycleState.DECOMMISSIONED, LegalEntityLifecycleState.ACTIVE)


if __name__ == "__main__":
    unittest.main()
