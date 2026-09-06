from typing import Protocol


class DatabaseProbe(Protocol):
    def ping(self) -> None: ...


def liveness() -> dict[str, str]:
    """Process liveness only; deliberately discloses nothing about backend state."""
    return {"status": "ok", "service": "baobab-erp"}


def readiness(database: DatabaseProbe) -> dict[str, str]:
    """Authenticated readiness probe including database connectivity."""
    database.ping()
    return {"status": "ready", "service": "baobab-erp"}
