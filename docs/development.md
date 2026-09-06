# Development

```bash
cp .env.example .env
./scripts/dev/bootstrap.sh
```

`scripts/dev/bootstrap.sh` installs `modules/` in editable mode and builds the OSGi
extension bundles with Maven. `scripts/dev/services.sh` (the Codespaces
`postStartCommand`) applies `db/migrations/` against `DATABASE_URL` when Postgres is
reachable.

## Running the full runtime

```bash
docker compose up -d
```

Brings up iDempiere (built from `idempiere/Dockerfile`, extension bundles included) and
PostgreSQL. See `docs/operations.md` for production requirements.

## Repository layout

| Path | Contents |
|---|---|
| `idempiere/` | Upstream pin, Dockerfile, OSGi extension bundles (Java/Maven) |
| `modules/` | Application-service layer (Python, framework-free) |
| `db/` | Postgres migrations and (empty, by policy) seed data for the `baobab` schema |
| `contracts/` | Event/API interface profiles this engine exposes |
| `migration/` | Scaffolding for a future legacy-ERP-source migration (currently unused; see `migration/README.md`) |
| `tests/` | unit, integration, contract, architecture, tenancy, security, migration, golden |
| `architecture/conformance.yaml` | Per-ADR implementation status |
| `docs/adr/` | Architecture Decision Records |

See `docs/testing.md` for what each `tests/` subdirectory covers and how to run it.
