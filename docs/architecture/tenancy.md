# Tenancy and Organisation Context

Baobab's concepts and ERPNext records are related but not interchangeable.

| Baobab concept | ERP representation | Rule |
|---|---|---|
| Tenant | Frappe site plus `Baobab Tenant Mapping` | Isolation boundary; carries immutable `tenant_id` |
| Organisation | Mapping record | May span or group legal entities; does not automatically become a Company |
| Legal Entity | Usually ERPNext `Company` through a mapping | Default tenant boundary, never the definition of tenant |
| Business Unit | Cost Centre, Accounting Dimension, or mapping | Chosen according to accounting/reporting semantics |
| Function | Cost Centre or mapping | Do not manufacture a Company |
| Team | Frappe roles/user permissions or mapping | Not an accounting entity by default |
| User | Frappe `User` plus canonical identity mapping | Frappe owns credentials; Baobab owns canonical identity reference |
| Membership | Baobab identity integration | Grants context; must not be inferred from email domain |
| Role | Frappe `Role` | Mapped from canonical roles where required |
| Permission | Frappe permissions and user permissions | Enforced locally after authentication and context resolution |

Requests carrying Baobab context must supply both `X-Baobab-Tenant-ID` and `X-Baobab-Entity-ID`. The app verifies their active mapping and fails closed on incomplete or contradictory values. Native Desk requests remain governed by Frappe's own session and permission model.

The canonical registry remains `nabhold/shared/contracts/legal-entity/registry.yaml`. This repository stores references and mappings, not a competing copy.
