import json
from typing import Protocol

from events.envelope import EventEnvelope
from security.signing import verify_signature


class InboxStore(Protocol):
    """Backing store for the idempotent event inbox (ADR-ERP-006)."""

    def exists(self, event_id: str) -> bool: ...

    def record_received(self, envelope: EventEnvelope, payload_json: str) -> None: ...


class InvalidSignatureError(Exception):
    pass


def receive(body: bytes, signature: str, secret: str, store: InboxStore) -> EventEnvelope:
    """Verify, deduplicate, and record an inbound event. Returns the envelope either way.

    Duplicate delivery of an already-seen event_id is not an error: at-least-once
    delivery means callers must expect and safely ignore duplicates.
    """
    if not verify_signature(body, signature, secret):
        raise InvalidSignatureError("Invalid event signature")

    envelope = EventEnvelope.from_dict(json.loads(body))
    if store.exists(envelope.event_id):
        return envelope

    payload_json = json.dumps(envelope.payload, separators=(",", ":"), sort_keys=True)
    store.record_received(envelope, payload_json)
    return envelope
