-- Backs modules/inbox (ADR-ERP-006). event_id is the idempotency key: a duplicate
-- delivery of an already-recorded event_id is detected here, never reprocessed.
CREATE TABLE baobab.event_inbox (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL UNIQUE,
    event_type      TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    source_engine   TEXT NOT NULL,
    correlation_id  TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    payload_json    JSONB NOT NULL,
    status          TEXT NOT NULL DEFAULT 'received'
                        CHECK (status IN ('received', 'processed', 'failed')),
    last_error      TEXT,
    received_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at    TIMESTAMPTZ
);
