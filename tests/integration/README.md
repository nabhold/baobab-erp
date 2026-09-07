Integration tests exercise the Postgres-backed stores in `modules/*/postgres_store.py`
and the HTTP application layer in `modules/application/server.py` against a real
PostgreSQL database with `db/migrations/` applied. They skip cleanly (not fail) when
`DATABASE_URL` isn't set, so `./scripts/validate.sh` stays green without a database.

```bash
export DATABASE_URL=postgresql://baobab:baobab@localhost:5432/baobab_test
./db/migrate.sh
PYTHONPATH=modules python -m unittest discover -s tests/integration -p 'test_*.py'
```

Each test creates its own uniquely-named rows and cleans them up in `tearDown`/
`addCleanup`, so tests can run repeatedly against a persistent database without
manual resets.
