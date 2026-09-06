Migration rehearsal tests (Phase 24) run the pipeline in `migration/` against a restored
ERPNext snapshot and assert on record counts, rejections, and financial/inventory
differences. Empty until `migration/` has real extraction/transform/import code to test,
which in turn needs a real ERPNext source system — see `migration/README.md`.
