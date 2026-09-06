"""Thin seam over iDempiere's own REST/JSON-RPC API.

The application layer (`modules/application`) speaks canonical contracts; this module
is the only place that knows iDempiere's actual API shape, per ADR-ERP-005. No other
module should import this one directly for business logic -- go through
`modules/application` so the canonical/native boundary stays in one place.

This is a foundation-stage seam: it defines the interface the application layer needs
and a placeholder that fails loudly, rather than a partially-correct HTTP client. Wiring
a real implementation is tracked in architecture/conformance.yaml against ADR-ERP-005.
"""

from dataclasses import dataclass
from typing import Any, Protocol


class IdempiereClientError(Exception):
    pass


class IdempiereClient(Protocol):
    def get_record(self, table: str, record_id: int) -> dict[str, Any]: ...

    def create_record(self, table: str, fields: dict[str, Any]) -> int: ...

    def update_record(self, table: str, record_id: int, fields: dict[str, Any]) -> None: ...


@dataclass(frozen=True, slots=True)
class IdempiereEndpoint:
    base_url: str
    ad_client_id: int
    ad_org_id: int


class UnconfiguredIdempiereClient:
    """Raised-on-use placeholder until an HTTP-backed client is approved and wired."""

    def __init__(self, endpoint: IdempiereEndpoint) -> None:
        self._endpoint = endpoint

    def get_record(self, table: str, record_id: int) -> dict[str, Any]:
        raise IdempiereClientError(f"No iDempiere client wired for {self._endpoint.base_url}")

    def create_record(self, table: str, fields: dict[str, Any]) -> int:
        raise IdempiereClientError(f"No iDempiere client wired for {self._endpoint.base_url}")

    def update_record(self, table: str, record_id: int, fields: dict[str, Any]) -> None:
        raise IdempiereClientError(f"No iDempiere client wired for {self._endpoint.base_url}")
