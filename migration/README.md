# Migration Tooling

This directory is the entry point for a semantic ERP migration *from a live ERPNext
deployment into iDempiere*, per the Baobab migration programme (Phases 1, 10–17, 21–26).

## Current state: scaffolding, not in use

No live ERPNext deployment has ever existed for Baobab. This repository previously
carried an ERPNext/Frappe foundation-stage scaffold with no site ever initialised, no
tenant ever onboarded, and no financial or master data ever created — see
`docs/migration/erpnext-removal-report.md`. There is therefore nothing to extract yet,
and every subdirectory here is an empty, documented placeholder rather than working
tooling.

If a real ERPNext instance is stood up before Baobab reaches production and needs to be
migrated, start with Phase 1 (`docs/migration/erpnext-inventory.yaml` and friends,
per the audit checklist) and build the pipeline stage by stage:

```text
ERPNext → extraction/ → staging/ → transforms/ → (validate) → imports/ → iDempiere
                                                                  │
                                                            reconciliation/
                                                                  │
                                                              cutover/
```

## Subdirectories

| Directory | Purpose |
|---|---|
| `extraction/` | Pulls records from a live ERPNext source into a portable format |
| `staging/` | Temporary staging tables/files (`stg_party`, `stg_product`, ...) — never a permanent domain model |
| `transforms/` | ERPNext → canonical → iDempiere field-level transformation specs and code |
| `imports/` | Import adapters that create/update iDempiere records from validated staging data |
| `reconciliation/` | Migration-specific reconciliation (counts, control totals, trial balance) — distinct from the ongoing operational reconciliation in `modules/reconciliation` |
| `cutover/` | Freeze, drain, final-delta, and go-live runbooks and scripts |

Do not add speculative code to these directories ahead of a real source system to migrate
from; empty, well-documented scaffolding is the honest state until then.
