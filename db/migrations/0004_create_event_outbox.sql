-- Backs modules/outbox (ADR-ERP-006). A row is inserted in the same transaction as the
-- operational change it describes; a scheduler drains status IN ('pending', 'retry').
CREATE TABLE baobab.event_outbox (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL UNIQUE,
    event_type      TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    tenant_id       TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    correlation_id  TEXT NOT NULL,
    payload_json    JSONB NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'retry', 'delivered', 'dead_letter')),
    attempts        INTEGER NOT NULL DEFAULT 0,
    last_error      TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX event_outbox_pending_idx ON baobab.event_outbox (status) WHERE status IN ('pending', 'retry');
