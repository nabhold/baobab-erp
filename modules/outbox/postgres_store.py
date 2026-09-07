"""Postgres-backed OutboxStore against baobab.event_outbox.

See db/migrations/0004_create_event_outbox.sql. `record()` deliberately does not
commit -- it must run inside the caller's own transaction so the outbox row and the
operational change it describes commit or roll back together (ADR-ERP-006). The
other methods are independent units of work run by the dispatcher and commit
themselves.
"""

import json
from dataclasses import dataclass

import psycopg

from events.envelope import EventEnvelope


@dataclass(frozen=True, slots=True)
class PostgresOutboxRecord:
    name: str
    attempts: int
    status: str
    envelope: EventEnvelope


class PostgresOutboxStore:
    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def record(self, envelope: EventEnvelope) -> None:
        """Must be called within the caller's own transaction; does not commit."""
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO baobab.event_outbox
                    (event_id, event_type, schema_version, tenant_id, entity_id,
                     correlation_id, payload_json, occurred_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    envelope.event_id,
                    envelope.event_type,
                    envelope.schema_version,
                    envelope.tenant_id,
                    envelope.entity_id,
                    envelope.correlation_id,
                    json.dumps(envelope.payload, separators=(",", ":"), sort_keys=True),
                    envelope.occurred_at,
                ),
            )

    def pending(self, limit: int = 100) -> list[PostgresOutboxRecord]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT event_id, event_type, schema_version, tenant_id, entity_id,
                       correlation_id, payload_json, occurred_at, attempts, status
                FROM baobab.event_outbox
                WHERE status IN ('pending', 'retry')
                ORDER BY occurred_at
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()
        self._connection.commit()

        records = []
        for row in rows:
            (event_id, event_type, schema_version, tenant_id, entity_id, correlation_id, payload_json,
             occurred_at, attempts, status) = row
            envelope = EventEnvelope(
                event_id=str(event_id),
                event_type=event_type,
                schema_version=schema_version,
                occurred_at=occurred_at,
                source="baobab-erp",
                correlation_id=correlation_id,
                tenant_id=tenant_id,
                entity_id=entity_id,
                payload=payload_json,
            )
            records.append(
                PostgresOutboxRecord(name=str(event_id), attempts=attempts, status=status, envelope=envelope)
            )
        return records

    def mark_delivered(self, name: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "UPDATE baobab.event_outbox SET status = 'delivered' WHERE event_id = %s::uuid",
                (name,),
            )
        self._connection.commit()

    def mark_retry(self, name: str, attempts: int, error: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE baobab.event_outbox
                SET status = 'retry', attempts = %s, last_error = %s
                WHERE event_id = %s::uuid
                """,
                (attempts, error, name),
            )
        self._connection.commit()

    def mark_dead_letter(self, name: str, attempts: int, error: str) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE baobab.event_outbox
                SET status = 'dead_letter', attempts = %s, last_error = %s
                WHERE event_id = %s::uuid
                """,
                (attempts, error, name),
            )
        self._connection.commit()
