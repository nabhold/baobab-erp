# Deployment

`compose.yaml` provides the runtime baseline (Phase 4): a `postgres` service, an
`idempiere` service built from `idempiere/Dockerfile` (pins the upstream image, stages
in the Baobab OSGi extension bundles), a one-shot `baobab-db-migrate` service that
applies `db/migrations/` before anything else starts, a `baobab-app` service built from
`modules/Dockerfile` exposing the HTTP application layer
(`modules/application/server.py`: `/health/live`, `/health/ready`,
`POST /events/inbound`), and a `baobab-dispatch-worker` service (same image) that
periodically invokes `modules/application/dispatch_worker.py` to drain the event
outbox.

`modules/application/dispatch_worker.py` (outbox delivery) runs to completion and exits
by design -- it is not itself a long-lived daemon. The `baobab-dispatch-worker` Compose
service supplies the periodic invocation (`modules/scripts/dispatch_worker_loop.sh`, a
plain sleep loop configurable via `BAOBAB_DISPATCH_INTERVAL_SECONDS`, default 60s): the
loop is deployment configuration, not application code, and a failed tick is logged and
retried on the next tick rather than crashing the loop. A non-Compose deployment can
instead point cron or a systemd timer directly at `python -m application.dispatch_worker`
on the same schedule.

## Production requirements

1. Build images from a reviewed commit and immutable upstream pins
   (`upstream.lock.yaml`).
2. Replace every placeholder secret; store secrets outside Git.
3. Terminate TLS before iDempiere or `baobab-app`, or in front of an approved reverse
   proxy; iDempiere itself requires HTTPS from version 9 onward.
4. Restrict PostgreSQL to the private application network.
5. Back up the database (`adempiere` and `baobab` schemas together) and test restore
   before promoting a release.
6. Apply `db/migrations/` as a controlled pre-deployment step (`baobab-db-migrate` in
   Compose, or `db/migrate.sh` directly).
7. `modules/application/dispatch_worker.py` runs periodically via the
   `baobab-dispatch-worker` Compose service by default; a non-Compose deployment must
   schedule it itself (every minute or so) so outbox events actually get delivered.
8. Monitor HTTP health (`/health/ready`), outbox backlog and dead-letter count, database
   capacity, disk capacity, and certificate expiry.

Compose is the supported initial single-host deployment. Scaling to an orchestrator
requires an ADR backed by measured availability, capacity, or operational requirements
(ADR-ERP-013); production orchestration is owned by `nabhold/infrastructure`.

## Status

No production `EngineInstance` exists yet. `baobab-app`'s HTTP surface is currently
just health checks and the inbound event webhook -- see `architecture/conformance.yaml`
for what's still planned (a real iDempiere-facing client, LegalEntity accounting
configuration, and more).
