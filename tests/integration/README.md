Integration tests exercise `modules/` against a real PostgreSQL instance (with
`db/migrations` applied) and, once wired, a running iDempiere instance. They are not part
of the default fast unit-test run in CI; a future workflow job brings up
`compose.yaml` and runs them separately. Empty until the Postgres-backed store
implementations referenced in `modules/README.md` exist.
