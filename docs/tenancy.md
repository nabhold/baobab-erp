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

The canonical registry of tenants and legal entities remains owned by
`nabhold/baobab-cp`. This repository stores mappings and references, not a competing
copy.
