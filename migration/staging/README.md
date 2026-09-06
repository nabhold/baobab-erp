# Staging

Temporary migration staging models (`stg_party`, `stg_product`, `stg_warehouse`,
`stg_account`, `stg_open_ar`, `stg_open_ap`, `stg_inventory`, `stg_purchase_order`,
`stg_sales_order`, `stg_invoice`, `stg_payment`, per Phase 10). These are disposable
migration artefacts, not a permanent ERP domain model, and are dropped once a migration
batch is validated and imported. Empty until there is a real extraction to stage. See
`../README.md`.
