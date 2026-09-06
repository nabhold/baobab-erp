from enum import Enum, auto


class LegalEntityLifecycleState(Enum):
    """Onboarding states per ADR-ERP-019. Provisioning is never reduced to creating
    an AD_Client; readiness and accounting setup are explicit gates before ACTIVE."""

    REQUESTED = auto()
    ISOLATION_PROFILE_SELECTED = auto()
    ENGINE_INSTANCE_ASSIGNED = auto()
    ACCOUNTING_CONFIGURED = auto()
    ACTIVE = auto()
    SUSPENDED = auto()
    DECOMMISSIONING = auto()
    DECOMMISSIONED = auto()


_ALLOWED_TRANSITIONS: dict[LegalEntityLifecycleState, set[LegalEntityLifecycleState]] = {
    LegalEntityLifecycleState.REQUESTED: {LegalEntityLifecycleState.ISOLATION_PROFILE_SELECTED},
    LegalEntityLifecycleState.ISOLATION_PROFILE_SELECTED: {LegalEntityLifecycleState.ENGINE_INSTANCE_ASSIGNED},
    LegalEntityLifecycleState.ENGINE_INSTANCE_ASSIGNED: {LegalEntityLifecycleState.ACCOUNTING_CONFIGURED},
    LegalEntityLifecycleState.ACCOUNTING_CONFIGURED: {LegalEntityLifecycleState.ACTIVE},
    LegalEntityLifecycleState.ACTIVE: {LegalEntityLifecycleState.SUSPENDED, LegalEntityLifecycleState.DECOMMISSIONING},
    LegalEntityLifecycleState.SUSPENDED: {LegalEntityLifecycleState.ACTIVE, LegalEntityLifecycleState.DECOMMISSIONING},
    LegalEntityLifecycleState.DECOMMISSIONING: {LegalEntityLifecycleState.DECOMMISSIONED},
    LegalEntityLifecycleState.DECOMMISSIONED: set(),
}


class InvalidLifecycleTransitionError(Exception):
    pass


def transition(
    current: LegalEntityLifecycleState,
    target: LegalEntityLifecycleState,
) -> LegalEntityLifecycleState:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidLifecycleTransitionError(f"Cannot move from {current.name} to {target.name}")
    return target
