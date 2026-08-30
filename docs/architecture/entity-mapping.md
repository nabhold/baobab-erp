# Canonical-to-ERPNext Mapping

`Baobab Entity Mapping` records link `{tenant_id, canonical_type, canonical_id}` to `{erpnext_doctype, erpnext_name}`. The native ERPNext record remains authoritative for ERP operations.

| Canonical identity | Normal ERPNext target | Notes |
|---|---|---|
| Legal Entity | Company | Explicit mapping; never match by display name |
| External buyer | Customer | Trade customer ID maps to Customer name |
| External seller/vendor | Supplier | Preserve source identity separately |
| Product/SKU | Item | Trade catalogue ownership remains with Trade where applicable |
| Stock location | Warehouse | Warehouse company must agree with tenant context |
| Person/worker | Employee | User link remains standard ERPNext behaviour |
| User identity | User | Authentication remains Frappe/approved IdP |
| Business Unit/Function | Cost Centre or Accounting Dimension | Decide based on reporting semantics |
| Initiative | Project | Canonical project mapping is explicit |
| Location | Warehouse, Branch, or custom mapping | Context determines the native target |

Mappings are unique within a tenant and are audit-tracked. Synchronisation code must resolve a mapping before mutating native documents and must never guess using human-readable names.
