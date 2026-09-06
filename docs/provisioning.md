# Provisioning

Per ADR-ERP-019, onboarding a legal entity is never reduced to creating an `AD_Client`.
`modules/provisioning.lifecycle.LegalEntityLifecycleState` models the required gates:

```text
REQUESTED
   → ISOLATION_PROFILE_SELECTED
   → ENGINE_INSTANCE_ASSIGNED
   → ACCOUNTING_CONFIGURED
   → ACTIVE
   ⇄ SUSPENDED
   → DECOMMISSIONING
   → DECOMMISSIONED (terminal)
```

`transition()` enforces the allowed edges and raises
`InvalidLifecycleTransitionError` on any attempt to skip a gate (for example, moving
straight from `REQUESTED` to `ACTIVE` without an assigned `EngineInstance` and configured
accounting). See `tests/unit/test_provisioning_lifecycle.py`.

## Status

This is the state machine only. The Control Plane calls that actually select an
`IsolationProfile`, assign an `EngineInstance`, and drive accounting configuration
(chart of accounts, fiscal calendar, tax setup — Phase 9) are not yet implemented; see
`architecture/conformance.yaml` against ADR-ERP-019.
