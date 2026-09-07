# Tenancy and Organisation Context

Baobab's concepts and iDempiere's records are related but not interchangeable
(ADR-ERP-002).

| Baobab concept | iDempiere representation | Rule |
|---|---|---|
| Tenant | `AD_Client` through a mapping (`baobab.tenant_mapping`) | Isolation boundary; carries immutable `tenant_id`; never assumed equal to `AD_Client_ID` |
| Legal Entity | `AD_Org` through a mapping | Default tenant sub-boundary, never the definition of tenant |
| Market | Its own canonical concept via the Control Plane | Never assumed equal to `AD_Org` or a deployment region |
| Business Unit | Accounting dimension or mapping | Chosen according to accounting/reporting semantics |
| User | iDempiere `AD_User` plus canonical identity mapping | iDempiere owns credentials; Baobab owns the canonical identity reference (`modules/identity`) |
| Role / Permission | iDempiere `AD_Role` and native permissions | Enforced locally after authentication and context resolution |

Requests carrying Baobab context must supply both a tenant identifier and a legal-entity
identifier. `modules/context` resolves them against `baobab.tenant_mapping` and fails
closed on incomplete, inactive, or unresolved values — it never defaults or guesses. See
`tests/tenancy/test_context_resolver.py` for the fail-closed cases this is tested against,
including a same-shape-different-tenant negative case.

`modules/context.resolve_tenant` is the reverse direction: given the `AD_Client_ID`/
`AD_Org_ID` a piece of iDempiere-native code is already running under, resolve the
Baobab tenant/legal-entity that owns it (`GET /context/resolve-tenant`). This exists
because `baobab.tenant_mapping` also carries a unique index on
`(ad_client_id, ad_org_id) WHERE status = 'active'`
(`db/migrations/0006_add_tenant_mapping_native_unique_index.sql`) — the same fail-closed
guarantee as the forward direction, just entered from the other side. It's what lets
`idempiere/extensions/org.nabhold.baobab.erp.events` derive the correct tenant per
record rather than assuming one tenant for an entire iDempiere process, which would be
wrong under the default shared-instance topology (ADR-ERP-003).

The canonical registry of tenants and legal entities remains owned by
`nabhold/baobab-cp`. This repository stores mappings and references, not a competing
copy.
