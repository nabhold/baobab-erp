# Contributing

Use feature branches and pull requests. Never edit code under an installed upstream `frappe` or `erpnext` checkout. A required upstream change must first be tested as a normal Frappe extension; only an unavoidable fork may be proposed through an ADR.

Before submitting:

```bash
./scripts/validate.sh
cd .bench && bench --site baobab.localhost run-tests --app baobab_erp
```

Changes to contracts must be backward compatible within a major version. Event fields are additive; consumers must ignore unknown fields. Breaking changes require a new schema major version and an ADR.

Commit messages follow Conventional Commits. Never commit secrets, tenant data, database dumps, Bench sites, generated assets, or upstream source trees.
