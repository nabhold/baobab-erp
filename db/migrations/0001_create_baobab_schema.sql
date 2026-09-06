-- Baobab-owned schema, separate from iDempiere's own tables. No other engine is granted
-- access to either schema; this repository's application services are the only reader/
-- writer of `baobab`. See ADR-ERP-001, ADR-ERP-007.
CREATE SCHEMA IF NOT EXISTS baobab;
