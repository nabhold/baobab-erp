# Deployment

`compose.yaml` provides the runtime baseline (Phase 4): a `postgres` service, an
`idempiere` service built from `idempiere/Dockerfile` (pins the upstream image, stages
in the Baobab OSGi extension bundles), a one-shot `baobab-db-migrate` service that
applies `db/migrations/` before anything else starts, and a `baobab-app` service built
from `modules/Dockerfile` exposing the HTTP application layer
(`modules/application/server.py`: `/health/live`, `/health/ready`,
`POST /events/inbound`).

`modules/application/dispatch_worker.py` (outbox delivery) is not a compose service --
it runs to completion and exits, meant to be invoked periodically by an external
scheduler (cron, a systemd timer) rather than as a long-lived daemon.

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
7. Schedule `modules/application/dispatch_worker.py` to run periodically (every minute
   or so) so outbox events actually get delivered.
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
