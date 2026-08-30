# Deployment

`deploy/compose.yaml` provides the minimum complete Frappe topology: MariaDB, Redis cache, Redis queue, backend, frontend proxy, websocket service, short/default worker, long worker, scheduler, configurator, and one-time site creation.

## Production requirements

1. Build the image from a reviewed commit and immutable upstream pins.
2. Replace every placeholder secret; store secrets outside Git.
3. Terminate TLS before the frontend container and preserve trusted proxy headers.
4. Restrict MariaDB and Redis to the private application network.
5. Back up database, site files, `site_config.json`, and encryption keys together.
6. Run `bench migrate` as a controlled pre-deployment operation.
7. Test restore and rollback before promoting a release.
8. Monitor HTTP health, queue depth, failed jobs, scheduler activity, database capacity, disk capacity, and certificate expiry.

`live` is unauthenticated and reports process liveness only. `ready` requires authentication and checks database connectivity. Infrastructure should use a dedicated, narrowly permissioned probe identity if authenticated readiness is required remotely.

Compose is the supported initial single-host deployment. Scaling to an orchestrator requires an ADR backed by measured availability, capacity, or operational requirements.
