# Deployment

`compose.yaml` provides the iDempiere + PostgreSQL runtime baseline (Phase 4): a
`postgres` service and an `idempiere` service built from `idempiere/Dockerfile`, which
pins the upstream image and stages in the Baobab OSGi extension bundles.

## Production requirements

1. Build the image from a reviewed commit and immutable upstream pins
   (`upstream.lock.yaml`).
2. Replace every placeholder secret; store secrets outside Git.
3. Terminate TLS before iDempiere or in front of an approved reverse proxy; iDempiere
   itself requires HTTPS from version 9 onward.
4. Restrict PostgreSQL to the private application network.
5. Back up the database (`adempiere` and `baobab` schemas together) and test restore
   before promoting a release.
6. Apply `db/migrations/` as a controlled pre-deployment step (`db/migrate.sh`).
7. Monitor HTTP health, outbox backlog and dead-letter count, database capacity, disk
   capacity, and certificate expiry.

Compose is the supported initial single-host deployment. Scaling to an orchestrator
requires an ADR backed by measured availability, capacity, or operational requirements
(ADR-ERP-013); production orchestration is owned by `nabhold/infrastructure`.

## Status

No production `EngineInstance` exists yet. The application-service layer in `modules/`
does not yet expose an HTTP server (no web framework has been selected), so there is
nothing beyond iDempiere and PostgreSQL to operate today — see
`architecture/conformance.yaml`.
