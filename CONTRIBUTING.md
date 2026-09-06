# Contributing

Use feature branches and pull requests.

Never fork iDempiere core to make a change. Baobab behaviour belongs in an OSGi bundle
under `idempiere/extensions/` or an application-service module under `modules/`, using
supported extension points. An unavoidable upstream patch requires an ADR first (see
`idempiere/patches/README.md`).

Before submitting:

```bash
./scripts/validate.sh
```

This runs the unit/security/tenancy/contract/architecture test suites (against
`modules/` on `PYTHONPATH`, no install needed), validates every tracked JSON file,
builds the OSGi extension bundles with Maven, and validates the Compose model.

Changes to `contracts/` must be backward compatible within a major version. Event fields
are additive; consumers must ignore unknown fields. Breaking changes require a new schema
major version and an ADR.

Changes to `db/migrations/` are append-only: add a new numbered file, never edit a
previously-applied one.

Commit messages follow Conventional Commits. Never commit secrets, tenant data, database
dumps, or build output (`target/`).
