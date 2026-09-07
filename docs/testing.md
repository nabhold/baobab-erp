# Testing Strategy

| Layer | Purpose | Command |
|---|---|---|
| `tests/unit/` | Pure logic: envelope parsing, mapping resolution, outbox/inbox behaviour, provisioning lifecycle | `PYTHONPATH=modules python -m unittest discover -s tests/unit` |
| `tests/security/` | Signing/verification | `PYTHONPATH=modules python -m unittest discover -s tests/security` |
| `tests/tenancy/` | Context resolution, cross-tenant isolation, fail-closed cases | `PYTHONPATH=modules python -m unittest discover -s tests/tenancy` |
| `tests/contract/` | Every example event validates against both the JSON Schema and `EventEnvelope` | `PYTHONPATH=modules python -m unittest discover -s tests/contract` |
| `tests/architecture/` | Fitness functions, e.g. no stray legacy-ERP-framework references (see `tests/architecture/test_no_erpnext_dependency.py`) | `PYTHONPATH=modules python -m unittest discover -s tests/architecture` |
| `tests/integration/` | Postgres-backed stores and the HTTP application layer against a real database (and, once wired, iDempiere) | `DATABASE_URL=... PYTHONPATH=modules python -m unittest discover -s tests/integration` (skips cleanly without `DATABASE_URL`) |
| `tests/migration/` | Migration rehearsals against a restored snapshot of the legacy ERP source | Not yet runnable — needs a real source system |
| `tests/golden/` | End-to-end procurement/sales/inventory/multi-currency flows | Not yet runnable — needs a wired iDempiere client |

`./scripts/validate.sh` runs everything that is currently runnable (unit, security,
tenancy, contract, architecture, JSON validation, the Maven build, and a Compose config
check) in one command; it is what CI runs.

Tests to add before promoting a feature from an extension point to a production flow:
duplicate delivery, retry exhaustion, missing tenant context, contradictory tenant/entity
mappings, cross-tenant access attempts, permission denial, schema-version compatibility,
and transactional outbox atomicity — most of these have at least one case under
`tests/unit/`/`tests/tenancy/` (fakes) and `tests/integration/` (a real database); extend
those rather than writing a parallel suite.
