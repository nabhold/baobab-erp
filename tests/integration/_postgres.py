"""Shared helper for tests/integration/: skip cleanly when there's no database to
run against, rather than failing. db/migrate.sh must have been run against
DATABASE_URL already; these tests don't apply migrations themselves.
"""

import os
import unittest

import psycopg


def require_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise unittest.SkipTest("DATABASE_URL not set; skipping Postgres integration test")
    return database_url


def connect() -> psycopg.Connection:
    return psycopg.connect(require_database_url())
