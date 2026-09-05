# ADR-ERP-003 — ERP EngineInstance Isolation, Regional Deployment and Data Residency

**Status:** Accepted  
**Decision class:** ERP / Infrastructure / Isolation / Multi-Region / Resilience / Data Residency  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/infrastructure`, `nabhold/shared`  
**Parent ADRs:** ADR-ERP-001, ADR-ERP-002  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL support multiple independently deployable `EngineInstance` resources and SHALL use `IsolationProfile` as the canonical policy governing how tenants, legal entities and markets are physically and logically isolated.

Baobab SHALL NOT establish either of these extremes as universal policy:

```text
one global iDempiere instance for everyone
```

or:

```text
one iDempiere deployment for every tenant
```

Instead:

> **Isolation shall be proportional to legal, regulatory, security, sovereignty, availability, scale and commercial requirements.**

The architecture SHALL permit a workload to evolve through isolation tiers without changing its canonical business identity.

For example:

```text
Shared EngineInstance
       ↓
Dedicated Client
       ↓
Dedicated EngineInstance
       ↓
Dedicated Regional EngineInstance
       ↓
Regulated / Sovereign EngineInstance
```

`Tenant`, `LegalEntity`, `Market`, `EngineInstance`, `DeploymentRegion` and `IsolationProfile` SHALL remain distinct concepts.

---

# 2. Architectural objective

The platform must support an organisation that starts with:

```text
South Africa
```

and later operates in:

```text
Uganda
Kenya
Rwanda
Tanzania
Zambia
Botswana
Namibia
European markets
Middle Eastern markets
```

without redesigning ERP tenancy.

Likewise, an organisation may initially be small enough to share infrastructure and later require dedicated infrastructure because of:

- transaction volume;
- regulatory requirements;
- data residency;
- contractual requirements;
- acquisition;
- divestiture;
- performance;
- security classification;
- geographic latency;
- operational autonomy.

The architecture SHALL accommodate this progression.

---

# 3. Engine versus EngineInstance

The canonical:

```text
Engine
```

represents the logical capability implementation.

Example:

```text
Engine
    code: baobab-erp
    implementation: iDempiere
```

An:

```text
EngineInstance
```

represents a deployed operational instance.

Therefore:

```text
Baobab ERP Engine
        │
        ├── ERP-AF-SOUTH-01
        ├── ERP-AF-EAST-01
        ├── ERP-EU-WEST-01
        └── ERP-THAMANI-01
```

SHALL all represent instances of the same canonical ERP Engine.

---

# 4. EngineInstance SHALL be a first-class Control Plane resource

An EngineInstance SHALL NOT merely be a hostname stored in application configuration.

The Control Plane SHALL model it explicitly.

Conceptually:

```text
EngineInstance

id
engine_id
code
status
environment
deployment_region
jurisdiction
isolation_profile
endpoint_reference
version
configuration_version
capacity_class
residency_policy
health_state
provisioned_at
activated_at
draining_at
retired_at
```

Sensitive credentials SHALL not be stored directly in this record.

Only secret references SHALL be permitted.

---

# 5. DeploymentRegion

Baobab SHALL introduce or formally recognise `DeploymentRegion` as an infrastructure concept distinct from `Market`.

A DeploymentRegion answers:

> Where is this workload physically/logically hosted?

Examples:

```text
AWS af-south-1
AWS eu-west-1
future AWS region
private sovereign infrastructure
other approved cloud region
```

A Market answers:

> Where does the business operate commercially?

These SHALL never be conflated.

---

# 6. Jurisdiction

Jurisdiction SHALL be modelled separately where legal/regulatory applicability cannot be inferred safely from Market or DeploymentRegion.

Conceptually:

```text
Market
    South Africa

Jurisdiction
    Republic of South Africa

DeploymentRegion
    AWS Africa (Cape Town)
```

These may often correlate.

They are not identical.

---

# 7. Why this separation matters

Consider:

```text
LegalEntity:
    Thamani

Market:
    Uganda

ERP Deployment:
    Cape Town
```

This may be entirely legitimate.

Therefore:

```text
Market Uganda
```

does not imply:

```text
ERP must physically run in Uganda
```

unless a residency or regulatory policy requires it.

Likewise:

```text
AWS Cape Town
```

does not mean:

```text
Market South Africa
```

---

# 8. Isolation dimensions

ERP isolation SHALL be evaluated across multiple dimensions.

At minimum:

```text
runtime
database
tenant/client
network
credentials
encryption
backup
deployment region
administrative access
observability
event routing
secrets
availability
```

Calling an instance "isolated" without specifying these dimensions is insufficient.

---

# 9. IsolationProfile

`IsolationProfile` SHALL represent a canonical policy bundle.

It SHALL describe required isolation rather than merely naming infrastructure.

Initial ERP profiles SHALL include at least:

```text
ERP_SHARED_CLIENT
ERP_SHARED_INSTANCE_DEDICATED_CLIENT
ERP_DEDICATED_INSTANCE
ERP_DEDICATED_REGIONAL
ERP_REGULATED
```

The first profile SHOULD be restricted and exceptional.

---

# 10. ERP_SHARED_CLIENT

This profile means multiple Baobab boundaries intentionally share an iDempiere Client.

Conceptually:

```text
EngineInstance
     │
     ▼
AD_Client
     │
     ├── AD_Org A
     └── AD_Org B
```

This SHALL NOT be the default for independent legal entities.

Use requires explicit approval under ADR-ERP-002.

---

# 11. ERP_SHARED_INSTANCE_DEDICATED_CLIENT

This SHALL be the default economical isolation profile for independent ordinary tenants where stronger infrastructure isolation is not required.

Topology:

```text
                    ERP-AF-SOUTH-01

                           │
                  iDempiere runtime
                           │
                     PostgreSQL
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    AD_Client A       AD_Client B       AD_Client C
```

The runtime and database infrastructure are shared.

Native iDempiere Client isolation separates tenant data.

---

# 12. Appropriate uses of shared-instance/dedicated-client

Suitable where:

- tenants have ordinary confidentiality requirements;
- jurisdictions permit shared infrastructure;
- workload is moderate;
- contractual requirements permit shared infrastructure;
- iDempiere Client isolation is sufficient;
- shared maintenance windows are acceptable;
- shared failure domain is acceptable.

---

# 13. Risks of shared-instance deployment

Shared instances introduce:

```text
shared runtime failure domain
shared database failure domain
shared upgrade schedule
shared maintenance window
resource contention
larger blast radius
administrative concentration
```

Therefore shared deployment is an economic optimisation, not a security principle.

---

# 14. ERP_DEDICATED_INSTANCE

A dedicated instance provides:

```text
Tenant / scoped boundary
          │
          ▼
Dedicated iDempiere runtime
          │
          ▼
Dedicated PostgreSQL database
```

No unrelated tenant business data resides within the same ERP application/database boundary.

---

# 15. Dedicated-instance triggers

Promotion SHOULD be considered when any of these arise:

```text
high transaction volume
material noisy-neighbour effects
contractual isolation
confidentiality classification
independent maintenance windows
M&A separation
divestiture readiness
tenant-specific upgrade requirements
major custom localisation
availability requirements
significant operational autonomy
```

---

# 16. ERP_DEDICATED_REGIONAL

This profile adds explicit regional placement.

Example:

```text
Thamani
   │
   └── East African ERP capability
             │
             ▼
       ERP-AF-EAST-01
             │
       regional deployment
             │
       dedicated database
```

The region is selected deliberately based on policy.

---

# 17. ERP_REGULATED

The strongest standard profile SHALL support requirements such as:

```text
dedicated runtime
dedicated database
dedicated encryption keys
restricted administrator set
regional residency
restricted backup geography
restricted network ingress
enhanced audit
enhanced retention
enhanced recovery
tenant-specific maintenance
```

This profile may eventually require dedicated cloud accounts or equivalent infrastructure boundaries.

---

# 18. IsolationProfile SHALL be policy, not implementation accident

The following is prohibited:

```text
Tenant happens to have its own server
therefore:
IsolationProfile = dedicated
```

Instead:

```text
IsolationProfile requires dedicated isolation
therefore:
provisioning creates appropriate infrastructure
```

Policy drives infrastructure.

Infrastructure does not define policy retrospectively.

---

# 19. IsolationProfile resolution

The effective profile MAY derive from:

```text
tenant requirement
legal entity requirement
market requirement
jurisdiction requirement
data classification
capability requirement
commercial subscription
regulatory requirement
operator override
```

The strongest applicable requirement SHALL prevail.

---

# 20. Isolation precedence

Conceptually:

```text
Tenant requires:
    shared-instance

Market requires:
    dedicated-regional

Effective:
    dedicated-regional
```

The weaker profile SHALL never override the stronger requirement merely because it is cheaper.

---

# 21. Default initial topology

For early Baobab deployment, assuming no contrary regulatory requirement:

```text
                         AWS Africa

                             │
                      ERP-AF-SOUTH-01
                             │
                     iDempiere 13 LTS
                             │
                        PostgreSQL
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
      AD_Client          AD_Client          AD_Client
       NABHOLD            THAMANI           ZURIBEANS
```

This provides reasonable infrastructure economy while maintaining native ERP Client separation.

---

# 22. The initial topology is not permanent architecture

The canonical architecture SHALL instead be understood as:

```text
                     BAOBAB ERP ENGINE
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        EngineInstance EngineInstance EngineInstance
```

Whether only one instance exists initially is an operational fact.

It is not a platform invariant.

---

# 23. Market expansion does not automatically provision infrastructure

When a tenant enters a new Market:

```text
Tenant Thamani
     │
     ├── Market ZA
     └── Market UG
```

the Control Plane SHALL evaluate whether the existing ERP binding remains suitable.

Possible outcome:

```text
ZA → ERP-AF-SOUTH-01
UG → ERP-AF-SOUTH-01
```

or:

```text
ZA → ERP-AF-SOUTH-01
UG → ERP-AF-EAST-01
```

The decision is policy-driven.

---

# 24. Regional deployment decision factors

Factors SHALL include:

- statutory residency;
- cross-border transfer restrictions;
- latency;
- customer contractual requirements;
- financial regulation;
- backup restrictions;
- disaster-recovery policy;
- operating cost;
- infrastructure availability;
- cloud service availability;
- ERP localisation;
- transaction volume;
- support capability.

---

# 25. Data residency policy

Every production EngineInstance SHALL have an explicit residency policy.

Conceptually:

```text
ResidencyPolicy

primary_region
permitted_regions[]
prohibited_regions[]
backup_regions[]
dr_regions[]
data_classes[]
jurisdictions[]
cross_border_transfer_policy
```

This may ultimately become its own canonical resource if required.

---

# 26. Residency applies to more than the primary database

Compliance SHALL consider:

```text
primary database
database replicas
backups
snapshots
object storage
logs
traces
dead-letter payloads
exports
support bundles
analytics copies
disaster-recovery copies
```

A database physically located in the correct country does not satisfy residency policy if its backups are copied indiscriminately elsewhere.

---

# 27. Canonical events and residency

Event-driven architecture SHALL also respect residency restrictions.

Events SHALL therefore minimise sensitive payloads.

Where policy requires:

```text
ERP event metadata
```

may leave a region while:

```text
sensitive financial payload
```

does not.

Canonical events SHALL not become an uncontrolled mechanism for cross-border data replication.

---

# 28. Event routing policy

Event routing MAY consider:

```text
source EngineInstance
tenant
legal entity
market
classification
residency policy
event type
consumer
```

A consumer SHALL only receive event data it is permitted to process.

---

# 29. Regional event transport

The architecture SHALL permit future regional event infrastructure.

Example:

```text
ERP-AF-SOUTH
      │
      ▼
Regional Event Transport
      │
      ▼
Approved Consumers
```

and:

```text
ERP-EU-WEST
      │
      ▼
EU Event Transport
```

without changing canonical event semantics.

Transport topology SHALL not leak into the event contract.

---

# 30. Database ownership

Every EngineInstance SHALL have explicit database ownership.

The normal relationship SHALL be:

```text
EngineInstance
       │
       ▼
ERP Database
```

For a shared instance:

```text
one ERP database
      │
      ├── Client A
      ├── Client B
      └── Client C
```

For dedicated:

```text
one ERP database
      │
      └── Client A
```

---

# 31. Database SHALL remain private

Only the ERP runtime, approved migration tooling, backup tooling and tightly controlled administration SHALL have database access.

Prohibited:

```text
Medusa → ERP PostgreSQL

Payload → ERP PostgreSQL

Digital Estate → ERP PostgreSQL

Analytics dashboard → unrestricted ERP PostgreSQL
```

---

# 32. Database technology

The ERP Engine SHALL use PostgreSQL as its supported production database baseline.

Database version SHALL be pinned and validated against the supported iDempiere release.

Database lifecycle SHALL be managed independently from MedusaJS and Payload CMS databases even where they use the same database technology.

---

# 33. Shared PostgreSQL server

Multiple unrelated Baobab engine databases MAY initially share managed infrastructure where risk and scale permit.

However:

```text
same PostgreSQL infrastructure
```

SHALL NOT mean:

```text
same database
same schema
same credentials
same ownership
```

Logical engine boundaries remain mandatory.

---

# 34. Higher isolation

Stronger profiles MAY require:

```text
dedicated database
dedicated database server/cluster
dedicated cloud account
dedicated encryption key
dedicated network
```

according to policy.

---

# 35. Encryption at rest

Production ERP persistence SHALL be encrypted at rest.

This includes, as applicable:

```text
database volumes
snapshots
backups
object storage
persistent queues
```

Regulated instances MAY require tenant- or instance-specific keys.

---

# 36. Encryption in transit

Traffic SHALL be encrypted across untrusted or separately controlled network boundaries.

At minimum:

```text
gateway → ERP integration layer
ERP runtime → managed database where required
cross-region traffic
backup transfer
administrative access
```

SHALL follow approved TLS/security policy.

---

# 37. Network isolation

Production topology SHOULD use private networking for:

```text
ERP runtime
PostgreSQL
internal integration endpoints
```

Public exposure SHALL terminate at approved ingress/gateway infrastructure.

The database SHALL never require a public endpoint for ordinary operation.

---

# 38. Administrative access

Administrative access SHALL be separated from application traffic.

Conceptually:

```text
Business traffic
      ↓
Gateway
      ↓
ERP API


Administrative traffic
      ↓
restricted operator path
      ↓
iDempiere administration
```

Administrative interfaces SHALL not be exposed merely because the public API is available.

---

# 39. EngineInstance endpoint

Consumers SHALL never persist a physical ERP hostname as business configuration.

They SHALL resolve:

```text
CapabilityBinding
        ↓
EngineInstance
        ↓
endpoint
```

This enables relocation.

---

# 40. Endpoint change

The Control Plane MAY change:

```text
erp-af-south-01.internal.old
```

to:

```text
erp-af-south-01.internal.new
```

without changing canonical EngineInstance identity if the logical instance remains the same.

Infrastructure address is an attribute.

It is not identity.

---

# 41. Instance replacement

If the logical deployment itself changes materially, a new EngineInstance SHALL normally be created.

Example:

```text
ERP-AF-SOUTH-01
       ↓ migration
ERP-AF-SOUTH-02
```

Historical events retain the original instance ID.

---

# 42. EngineInstance lifecycle

The canonical lifecycle SHALL include:

```text
requested
    ↓
provisioning
    ↓
configuring
    ↓
validating
    ↓
ready
    ↓
active
```

Operational transitions:

```text
active
  ├── degraded
  ├── maintenance
  ├── draining
  ├── suspended
  └── failed
```

Terminal:

```text
retired
```

---

# 43. `ready` versus `active`

`ready` means:

> The instance has passed technical validation.

`active` means:

> The Control Plane may route production capability bindings to it.

These SHALL remain separate.

---

# 44. Draining

`draining` means:

- no new bindings;
- controlled completion of in-flight operations;
- migration/replacement in progress;
- historical reads may remain possible where permitted.

This state is important for zero- or low-downtime migration.

---

# 45. Quarantine

A severe security or integrity incident MAY place an EngineInstance into:

```text
quarantined
```

if this state is adopted by the Control Plane lifecycle.

Quarantine SHALL prevent ordinary traffic regardless of existing CapabilityBindings.

---

# 46. CapabilityBinding is the routing authority

A tenant does not route to an ERP instance merely because a Mapping exists.

Routing requires:

```text
active CapabilityBinding
```

This distinction is essential.

A historical Mapping may remain forever.

A current CapabilityBinding determines where new operations go.

---

# 47. Example

Historical:

```text
Thamani
   → ERP-AF-SOUTH-01
   → AD_Client 1000000
```

Current:

```text
Thamani
   → ERP-THAMANI-01
   → AD_Client 1000000
```

Both mappings may exist.

Only the current CapabilityBinding determines new transaction routing.

---

# 48. Promotion from shared to dedicated

The platform SHALL support:

```text
ERP-AF-SOUTH-01
      │
      ├── NABHOLD
      ├── THAMANI
      └── ZURIBEANS
```

becoming:

```text
ERP-AF-SOUTH-01
      │
      ├── NABHOLD
      └── ZURIBEANS


ERP-THAMANI-01
      │
      └── THAMANI
```

without changing:

```text
Tenant ID
LegalEntity ID
Product canonical IDs
Supplier canonical IDs
Customer canonical IDs
```

---

# 49. Promotion workflow

The migration SHALL be orchestrated.

Suggested phases:

```text
assessment
    ↓
target provision
    ↓
configuration replication
    ↓
bulk data migration
    ↓
mapping preparation
    ↓
reconciliation
    ↓
write freeze / controlled delta
    ↓
final synchronization
    ↓
CapabilityBinding switch
    ↓
verification
    ↓
source drain
    ↓
source retirement
```

---

# 50. Migration SHALL be observable

Migration state SHALL be represented explicitly.

At minimum:

```text
migration_id
source_instance
target_instance
tenant/legal entity
state
started_at
cutover_at
completed_at
reconciliation_status
rollback_deadline
```

---

# 51. Migration SHALL not mutate canonical identity

This is an invariant.

Migration changes:

```text
EngineInstance
ExternalReference
Mapping
CapabilityBinding
```

It does not change:

```text
Tenant
LegalEntity
canonical business identities
```

unless a genuine business identity change occurs independently.

---

# 52. Rollback

Migration plans SHALL define rollback before cutover.

Rollback SHALL account for:

- transactions written after migration begins;
- mapping state;
- event publication;
- downstream projections;
- idempotency;
- reconciliation.

Simply restoring yesterday's database is not a migration rollback strategy.

---

# 53. Event behaviour during migration

Events SHALL retain the actual producing:

```text
engine_instance_id
```

During a migration, events may temporarily originate from source and target infrastructure according to the migration protocol.

Consumers SHALL rely on canonical entity identity and event idempotency, not hostname assumptions.

---

# 54. Split-brain prevention

At final cutover, Baobab SHALL ensure only one authoritative write path exists for a given capability/scope.

The following state is prohibited:

```text
Thamani
   ├── writes → ERP-AF-SOUTH-01
   └── writes → ERP-THAMANI-01
```

unless a specially designed dual-write migration protocol exists.

Ordinary operation SHALL have one authoritative write binding.

---

# 55. Read migration

Temporary dual-read strategies MAY be permitted for verification.

For example:

```text
authoritative read:
    target

verification read:
    source
```

Results may be compared during cutover.

Only one result is authoritative to consumers.

---

# 56. Regional expansion

Consider:

```text
Thamani
   │
   ├── South Africa
   └── Uganda
```

Initial:

```text
both markets
     ↓
ERP-AF-SOUTH-01
```

Later:

```text
South Africa
     ↓
ERP-AF-SOUTH-01

Uganda
     ↓
ERP-AF-EAST-01
```

This SHALL be possible through Market-scoped CapabilityBindings and Mappings.

---

# 57. Market-specific EngineInstances

Where one LegalEntity uses several regional instances, each business object SHALL have an unambiguous authoritative ERP home.

The platform SHALL not permit the same operational object to be independently authoritative in two ERP instances without an explicit distributed-domain design.

---

# 58. Object home

Future implementation MAY formalise:

```text
home_engine_instance_id
```

for appropriate canonical entities or mappings.

At minimum, authoritative MappingScope SHALL make the home unambiguous.

---

# 59. Cross-region business

Cross-region transactions SHALL be represented through explicit business processes.

Example:

```text
South African ERP context
          │
          ▼
canonical intercompany/interbranch process
          │
          ▼
East African ERP context
```

not direct cross-database SQL.

---

# 60. Data replication

Replication SHALL distinguish:

```text
operational replication
disaster-recovery replication
analytical replication
integration projection
```

These have different consistency and residency requirements.

They SHALL not be lumped together under “replication.”

---

# 61. No multi-master by default

ERP transactional databases SHALL not initially use multi-region active-active multi-master architecture.

Financial systems benefit from clear transactional authority.

Default:

```text
single authoritative write region
```

per EngineInstance.

---

# 62. Why active-active is rejected initially

Active-active ERP across regions introduces substantial complexity in:

- transaction ordering;
- sequences;
- accounting documents;
- conflict resolution;
- inventory;
- idempotency;
- database consistency;
- operational diagnosis.

Baobab SHALL introduce such complexity only if measurable business requirements justify it.

---

# 63. Availability architecture

Availability SHALL be considered independently from geographic distribution.

A highly available regional instance might use:

```text
multiple application nodes
        │
        ▼
single regional database authority
        │
        ├── standby
        └── backups
```

without becoming multi-region active-active.

---

# 64. Stateless application nodes

Where iDempiere deployment characteristics permit, application runtime nodes SHOULD minimise local persistent state.

Durable business state belongs in approved persistent services.

This makes replacement and scaling safer.

---

# 65. Horizontal scaling

EngineInstance capacity MAY evolve from:

```text
1 application node
```

to:

```text
N application nodes
```

without creating a new canonical EngineInstance if they collectively represent the same logical deployment boundary.

---

# 66. EngineInstance does not equal container

An EngineInstance may consist of:

```text
multiple containers
load balancer
database
cache
workers
monitoring
```

It represents the logical service deployment, not a single process.

---

# 67. Capacity classes

The Control Plane MAY define capacity classes such as:

```text
small
medium
large
xlarge
custom
```

but these SHALL remain infrastructure policies rather than business identities.

Scaling capacity SHALL not change canonical EngineInstance identity unless the deployment boundary itself changes.

---

# 68. Resource quotas

Shared instances SHALL define resource controls to mitigate noisy-neighbour risk.

Monitor at minimum:

```text
CPU
memory
database connections
storage
IOPS
background jobs
API rate
event volume
```

Persistent tenant-specific pressure MAY trigger dedicated-instance promotion.

---

# 69. Promotion criteria

A tenant SHOULD be evaluated for promotion when sustained utilisation materially affects other tenants or threatens SLOs.

Promotion policy SHOULD be measurable rather than political.

Examples:

```text
resource saturation
queue delay
database contention
storage growth
latency
availability impact
```

---

# 70. Service-level objectives

Each production EngineInstance SHALL have defined SLOs.

At minimum:

```text
availability
request success rate
latency
event publication delay
recovery objectives
```

Higher isolation tiers MAY receive stronger SLOs.

---

# 71. RPO

Every production instance SHALL define a Recovery Point Objective.

Example classes might eventually be:

```text
RPO-0
RPO-5m
RPO-15m
RPO-1h
```

Exact values SHALL be business-approved rather than guessed by engineering.

---

# 72. RTO

Likewise, Recovery Time Objective SHALL be explicit.

A system with backups but no agreed restoration time does not have a complete continuity architecture.

---

# 73. Backup policy

Production ERP databases SHALL have:

- automated backups;
- encrypted storage;
- retention policy;
- backup monitoring;
- off-host durability;
- restoration testing;
- documented ownership.

---

# 74. Backup isolation

A dedicated or regulated tenant MAY require dedicated backup artefacts.

Shared-instance backups necessarily contain several Clients.

Access controls SHALL therefore recognise that a shared-instance backup is highly sensitive multi-tenant data.

---

# 75. Restore implications for shared instances

A major disadvantage of shared databases is restore granularity.

Restoring:

```text
Client A
```

from a whole-instance backup can be more complicated than restoring a dedicated database.

This SHALL be considered when selecting IsolationProfile.

---

# 76. Point-in-time recovery

Production PostgreSQL SHOULD support PITR where the chosen hosting model permits it.

PITR SHALL be tested.

Configuration without restoration testing is insufficient.

---

# 77. Disaster-recovery topology

A typical future regional DR design MAY resemble:

```text
             PRIMARY REGION
                   │
             ERP Instance
                   │
             PostgreSQL
                   │
          replication/backups
                   │
                   ▼
             RECOVERY REGION
```

The recovery environment SHALL not automatically receive production traffic.

---

# 78. Active-passive preference

For regional disaster recovery, Baobab SHALL initially prefer:

```text
active-passive
```

over:

```text
active-active
```

unless an explicit later ADR justifies active-active.

---

# 79. DR failover is a Control Plane event

Failover SHALL update authoritative routing.

Conceptually:

```text
EngineInstance primary
       ↓ unavailable

DR activation
       ↓

EngineInstance state transition
       ↓

CapabilityBinding routing update
```

Consumers SHALL not maintain independent failover host lists.

---

# 80. DNS alone is insufficient authority

DNS may participate in failover.

However the Control Plane SHALL remain aware of which logical EngineInstance/deployment is authoritative.

Otherwise audit and event provenance become ambiguous.

---

# 81. Failover data integrity

Before promoting a recovery database, the operator or automation SHALL determine:

```text
last known replication position
potential data loss
RPO breach
pending events
outbox state
```

Financial systems SHALL not hide uncertainty during recovery.

---

# 82. Outbox recovery

Because canonical events are transactionally recorded with ERP changes, recovery procedures SHALL preserve or reconstruct unpublished outbox entries.

Failover SHALL not create silent event gaps.

---

# 83. Event replay after recovery

Event publishers SHALL support safe replay using immutable event IDs.

Consumers remain idempotent.

Therefore:

```text
duplicate event
```

is preferable to:

```text
lost financial event
```

provided consumers correctly deduplicate.

---

# 84. Regional outage

A regional ERP outage SHALL not automatically disable unrelated regional instances.

Example:

```text
ERP-AF-SOUTH-01 failed
```

SHALL not inherently disable:

```text
ERP-EU-WEST-01
```

This is a primary benefit of EngineInstance isolation.

---

# 85. Shared Control Plane dependency

The ERP architecture SHALL avoid making every transaction require a long synchronous round trip to a distant Control Plane if doing so materially reduces resilience.

Future signed Context and bounded mapping caches MAY permit safe local operation.

However cached authorization SHALL never broaden access.

---

# 86. Control Plane regional architecture

The eventual Control Plane deployment may itself become regional.

That decision is outside this ADR.

ERP SHALL depend only on the Control Plane contract, not its physical deployment topology.

---

# 87. Infrastructure provider abstraction

Baobab currently targets AWS as its principal production cloud.

However canonical EngineInstance contracts SHALL not use AWS resource identifiers as platform identity.

Correct:

```text
engine_instance_id = UUID
deployment_provider = aws
deployment_region = af-south-1
```

Incorrect:

```text
engine_instance_id = arn:aws:...
```

---

# 88. Cloud provider SHALL remain replaceable

An EngineInstance may eventually run on:

```text
AWS
another cloud
private infrastructure
sovereign cloud
```

without changing the semantics of:

```text
Tenant
LegalEntity
Capability
Mapping
Context
```

---

# 89. AWS account strategy

Initial deployments MAY share an AWS account according to infrastructure standards.

Higher IsolationProfiles MAY require:

```text
dedicated AWS account
```

or equivalent boundary.

Account separation SHALL therefore remain possible but SHALL not be required universally from day one.

---

# 90. Environment isolation

Production SHALL be isolated from:

```text
development
test
staging
```

At minimum:

```text
separate databases
separate credentials
separate secrets
separate endpoints
```

SHALL apply.

Production data SHALL not be casually copied to lower environments.

---

# 91. Environment is not Region

The following are separate dimensions:

```text
environment = production
region      = af-south
```

A production platform may have several regions.

A region may contain several environments.

---

# 92. EngineInstance identity includes environment semantically

A staging ERP deployment and production ERP deployment SHALL be different EngineInstances.

They shall never share the same canonical instance identity merely because they run the same version.

---

# 93. Naming convention

Human-readable EngineInstance codes SHOULD follow a predictable convention.

Example:

```text
ERP-AF-SOUTH-01
ERP-AF-EAST-01
ERP-EU-WEST-01
ERP-THAMANI-AF-SOUTH-01
```

The exact naming standard belongs in organisational infrastructure contracts.

UUID remains authoritative.

---

# 94. Version heterogeneity

Different EngineInstances MAY temporarily operate different supported patch versions during controlled rollout.

Example:

```text
ERP-AF-SOUTH-01
    iDempiere 13.x patch N

ERP-AF-EAST-01
    iDempiere 13.x patch N+1
```

Canonical APIs/events SHALL shield consumers from compatible implementation differences.

---

# 95. Version skew limits

Supported version skew SHALL be explicitly bounded.

The platform SHALL not permit indefinite divergence resulting in effectively different ERP products.

---

# 96. Rolling upgrade

Where topology permits, upgrades SHOULD minimise downtime through controlled:

```text
drain
upgrade
validate
activate
```

operations.

Financial integrity takes priority over nominal zero downtime.

---

# 97. Shared-instance upgrade consequence

All Clients on a shared instance share the underlying iDempiere version.

Therefore:

```text
Tenant A cannot remain on version X
while
Tenant B uses version Y
```

inside the same EngineInstance.

This is a material isolation trade-off.

---

# 98. Dedicated-instance advantage

Dedicated instances permit:

- independent maintenance;
- independent upgrade schedule;
- tenant-specific plugins;
- stronger blast-radius containment;
- independent capacity;
- independent recovery.

These benefits justify the higher cost for appropriate tenants.

---

# 99. Plugin policy

All plugins installed into a shared EngineInstance SHALL be compatible with every Client hosted there.

Tenant-specific unsafe plugins SHALL trigger evaluation for dedicated deployment.

One tenant SHALL not be permitted to destabilise shared ERP infrastructure through arbitrary extensions.

---

# 100. Localisation and regional instances

Regional localisation MAY influence instance placement.

For example:

```text
ERP-AF-EAST-01
```

may carry approved East African localisation plugins.

However:

```text
localisation set
```

and:

```text
DeploymentRegion
```

remain separate configuration concepts.

A localisation is a business/regulatory capability.

A region is infrastructure placement.

---

# 101. Shared localisation compatibility

Before adding a localisation plugin to a shared EngineInstance, operators SHALL assess whether it:

- alters shared schema;
- changes global behaviour;
- affects unrelated Clients;
- introduces incompatible dependencies;
- changes upgrade constraints.

If unsafe, dedicated or regional isolation SHALL be preferred.

---

# 102. Configuration drift

EngineInstance configuration SHALL be reproducible.

Manual production configuration outside governed mechanisms SHALL be minimised.

Drift detection SHOULD compare:

```text
desired configuration
        ↔
observed configuration
```

---

# 103. Infrastructure as code

Infrastructure resources SHALL be managed declaratively where practical.

This includes:

```text
network
compute
database
storage
secrets references
security groups
backup policy
monitoring
```

The exact IaC technology is governed by `nabhold/infrastructure`.

---

# 104. ERP master data is not infrastructure as code

The following distinction SHALL remain:

```text
Infrastructure configuration
        ≠
ERP business master data
```

Charts of accounts, suppliers, products and tax records are not ordinary Terraform-style infrastructure resources merely because they can technically be automated.

---

# 105. Secrets isolation

Every EngineInstance SHALL use independently addressable secret references.

A compromise of:

```text
ERP-AF-SOUTH-01
```

SHALL not automatically reveal credentials for:

```text
ERP-EU-WEST-01
```

---

# 106. Database credentials

Dedicated EngineInstances SHALL have dedicated database credentials.

Shared EngineInstances SHALL still use credentials exclusive to the ERP application, not credentials shared with Medusa or Payload.

---

# 107. Encryption key isolation

Higher IsolationProfiles MAY require:

```text
EngineInstance-specific key
```

or:

```text
tenant-specific key
```

where supported.

Key lifecycle SHALL be auditable.

---

# 108. Observability isolation

Metrics may be aggregated globally.

Logs and traces containing tenant-sensitive information SHALL respect data classification and residency.

Central observability SHALL not become a back door around residency policy.

---

# 109. Log residency

A regulated instance may require:

```text
ERP data in region A
logs in region A
backups in region A
```

not:

```text
ERP data in A
all logs copied globally
```

This SHALL be accounted for in ResidencyPolicy.

---

# 110. Audit residency

Financial and security audit data SHALL follow explicit retention and residency rules.

Audit durability may require stricter retention than ordinary application logs.

---

# 111. Monitoring scope

Control Plane SHALL track at minimum:

```text
EngineInstance availability
version
health state
deployment region
isolation profile
binding count
capacity indicators
last successful backup
last restore test
certificate/credential status where appropriate
```

---

# 112. Instance health does not equal tenant health

A shared instance may be healthy while one Client has configuration problems.

Therefore observability SHOULD distinguish:

```text
instance health
tenant ERP readiness
capability health
integration health
```

---

# 113. Tenant-specific circuit breaking

Repeated failures for one tenant SHOULD NOT necessarily disable the whole EngineInstance.

Integration architecture SHOULD permit tenant/context-specific circuit breakers where useful.

---

# 114. Rate limiting

Shared instances SHOULD support rate limiting or workload controls by:

```text
tenant
capability
service identity
```

to protect neighbouring tenants.

---

# 115. Maintenance windows

Every EngineInstance SHALL have an explicit maintenance policy.

Shared-instance tenants accept a shared maintenance boundary.

Dedicated tenants MAY receive independent schedules.

This distinction may eventually form part of the commercial product model.

---

# 116. Planned maintenance

Before maintenance:

```text
EngineInstance → maintenance_pending
```

may be recorded.

At execution:

```text
active
  ↓
draining
  ↓
maintenance
  ↓
validating
  ↓
active
```

where operational tooling supports these states.

---

# 117. Unplanned failure

Failure transition:

```text
active
  ↓
degraded
  ↓
failed
```

may trigger:

```text
retry
circuit break
DR decision
operator escalation
```

depending on severity.

---

# 118. Automated failover

Automated failover SHALL only be introduced when its correctness can be demonstrated.

For financial systems, a fast incorrect failover can be worse than a slower controlled recovery.

---

# 119. Recovery authority

Only approved automation or operators SHALL activate a recovery instance.

A digital estate SHALL never decide independently to redirect itself to an arbitrary ERP database.

---

# 120. Region evacuation

The architecture SHALL support future evacuation of an entire region.

Conceptually:

```text
ERP-AF-SOUTH-01
       ↓
migration / DR
ERP-AF-SOUTH-02 or approved recovery region
```

Canonical consumers remain insulated through bindings.

---

# 121. Data sovereignty and migration

Cross-region migration SHALL validate that moving:

```text
database
backups
logs
events
documents
```

is legally and contractually permitted before copying begins.

Technical capability does not imply legal permission.

---

# 122. Decommissioning

An EngineInstance SHALL not be destroyed immediately after migration.

Lifecycle:

```text
draining
   ↓
read-only retention if required
   ↓
backup/archive verification
   ↓
binding verification
   ↓
retired
   ↓
decommissioned
```

Retention policy governs final data destruction.

---

# 123. Retired EngineInstance metadata

Control Plane metadata for a retired EngineInstance SHALL remain available for historical resolution.

Historical event:

```text
engine_instance_id = retired instance UUID
```

must remain intelligible years later.

---

# 124. Deletion of EngineInstance identity

Canonical EngineInstance records that participated in production financial processing SHOULD never be hard-deleted merely because infrastructure has been destroyed.

Identity lineage must survive infrastructure lifecycle.

---

# 125. Infrastructure destruction

Destroying AWS resources is not equivalent to deleting the canonical EngineInstance.

The canonical record transitions to:

```text
retired
```

with infrastructure decommission metadata.

---

# 126. Disaster scenario — shared instance

Suppose:

```text
ERP-AF-SOUTH-01
```

fails.

Affected:

```text
Nabhold
Thamani
Zuribeans
```

if all three share it.

This is the explicit blast-radius cost of shared deployment.

---

# 127. Disaster scenario — dedicated instance

If:

```text
ERP-THAMANI-01
```

fails:

```text
Thamani affected
```

while:

```text
Nabhold
Zuribeans
```

may continue normally.

This is the primary operational benefit of physical isolation.

---

# 128. Isolation economics

Baobab SHALL recognise that stronger isolation costs more.

The architecture SHALL make that trade-off explicit rather than hiding it.

Conceptually:

```text
shared
    ↓
lower cost
larger blast radius

dedicated
    ↓
higher cost
smaller blast radius
greater autonomy
```

---

# 129. Commercial implication

Future Baobab product tiers MAY legitimately associate stronger isolation with higher commercial tiers.

However the platform SHALL never permit a lower commercial tier to violate mandatory legal or regulatory isolation.

Compliance overrides pricing.

---

# 130. No infrastructure cosplay

The architecture SHALL remain capable of Kubernetes and sophisticated regional orchestration without requiring them prematurely.

An EngineInstance may initially run using simpler container orchestration if production requirements are satisfied.

The canonical model SHALL not care whether the workload is implemented through:

```text
Docker Compose
ECS
Kubernetes
another approved orchestrator
```

---

# 131. Orchestrator abstraction

Consumers SHALL resolve an EngineInstance endpoint.

They SHALL not know whether the service runs in Kubernetes.

Thus:

```text
Kubernetes Namespace
```

is not a canonical business concept.

---

# 132. Future Kubernetes deployment

If Kubernetes is adopted:

```text
EngineInstance
       │
       ▼
Kubernetes deployment topology
```

not:

```text
EngineInstance = Kubernetes namespace
```

A namespace is an implementation resource.

---

# 133. Portability

Runtime packaging SHALL remain sufficiently portable that an ERP EngineInstance can be rebuilt in another approved environment.

This requires:

```text
immutable images
externalised configuration
externalised secrets
persistent database
repeatable provisioning
versioned plugins
```

---

# 134. Reproducibility

Given:

```text
engine version
plugin versions
configuration release
infrastructure definition
database backup
secret references
```

operators SHOULD be able to reconstruct an equivalent EngineInstance.

---

# 135. Golden image prohibition

Production servers SHALL not become irreplaceable pets manually maintained for years.

The deployment model SHALL favour replaceable infrastructure.

ERP data may be long-lived.

ERP application hosts should not be.

---

# 136. Security patching

Shared instances SHALL be patched according to platform policy even if one tenant would prefer indefinite delay.

Dedicated instances MAY allow controlled scheduling but SHALL still comply with maximum security-patch windows.

---

# 137. Vulnerability response

Critical vulnerability response MAY override ordinary maintenance windows.

Control Plane SHALL be capable of identifying all affected EngineInstances by:

```text
engine version
runtime version
plugin version
container digest
```

---

# 138. Software bill of materials

Every deployed ERP runtime SHOULD have an associated SBOM.

This is particularly important because the runtime combines:

```text
Java
iDempiere
OSGi bundles
database drivers
Baobab plugins
localisation plugins
container base
```

---

# 139. Instance provenance

Control Plane SHOULD be able to answer:

> Exactly what software is ERP-AF-SOUTH-01 running?

without logging into the server.

---

# 140. IsolationProfile mutation

Changing an IsolationProfile SHALL be a governed operation.

Example:

```text
shared_instance_dedicated_client
              ↓
dedicated_instance
```

may trigger infrastructure migration.

It SHALL not merely update a label.

---

# 141. Profile downgrade

Downgrading isolation:

```text
dedicated
   ↓
shared
```

SHALL require explicit approval and validation because it may reduce confidentiality, autonomy and resilience.

Automatic cost optimisation SHALL never silently downgrade isolation.

---

# 142. Profile upgrade

Increasing isolation MAY be automated more readily, but still requires:

```text
migration
reconciliation
cutover
validation
```

A policy update alone does not physically isolate existing data.

---

# 143. Policy drift

Control Plane SHOULD detect:

```text
required IsolationProfile
        ≠
observed deployment topology
```

Example:

```text
policy = dedicated
observed = shared
```

This SHALL be treated as a compliance defect.

---

# 144. Residency drift

Likewise:

```text
required region = A
observed region = B
```

SHALL trigger compliance alerts and potentially quarantine.

---

# 145. Desired versus observed state

The architecture SHOULD distinguish:

```text
desired state
observed state
```

for EngineInstances.

This lays the foundation for future reconciliation controllers without forcing Kubernetes-style control loops immediately.

---

# 146. Provisioning service boundary

Infrastructure provisioning SHALL belong outside the ERP business-domain plugin.

Conceptually:

```text
Control Plane
      │
      ▼
Provisioning / Infrastructure boundary
      │
      ▼
ERP deployment
```

iDempiere itself SHALL not provision AWS infrastructure.

---

# 147. ERP configuration boundary

After infrastructure provisioning:

```text
ERP provisioning service
```

may create/configure:

```text
AD_Client
AD_Org
roles
accounting schema
reference data
Baobab mappings
```

according to approved workflow.

Infrastructure and ERP business configuration remain separate phases.

---

# 148. Canonical events for EngineInstance lifecycle

The Control Plane SHOULD emit events such as:

```text
engine-instance.requested.v1
engine-instance.provisioned.v1
engine-instance.validated.v1
engine-instance.activated.v1
engine-instance.degraded.v1
engine-instance.draining.v1
engine-instance.retired.v1

capability-binding.activated.v1
capability-binding.reassigned.v1

isolation-profile.changed.v1
```

These are Control Plane events, not ERP domain events.

---

# 149. Migration events

Migration workflows SHOULD emit:

```text
engine-migration.started.v1
engine-migration.target-ready.v1
engine-migration.cutover-started.v1
engine-migration.cutover-completed.v1
engine-migration.reconciled.v1
engine-migration.completed.v1
engine-migration.failed.v1
```

This allows operational automation without database polling.

---

# 150. Auditability

For every production transaction, Baobab SHOULD eventually be capable of answering:

```text
Which tenant?
Which legal entity?
Which market?
Which ERP EngineInstance?
Which native Client?
Which version?
Which deployment region?
Which correlation trace?
```

That is the minimum level of lineage expected from a serious multi-region enterprise platform.

---

# 151. Rejected alternative — one permanent global ERP instance

**Rejected.**

It creates:

- excessive blast radius;
- residency limitations;
- latency constraints;
- upgrade coupling;
- difficult divestiture;
- difficult regulated workloads.

---

# 152. Rejected alternative — dedicated instance for everyone immediately

**Rejected as universal default.**

It creates unnecessary:

- compute cost;
- database cost;
- monitoring overhead;
- backup overhead;
- patching overhead;
- upgrade overhead.

Dedicated isolation remains available where justified.

---

# 153. Rejected alternative — region equals market

**Rejected.**

Commercial geography and infrastructure geography are different concerns.

---

# 154. Rejected alternative — region equals legal entity

**Rejected.**

A LegalEntity can operate in several markets and may use several regions.

---

# 155. Rejected alternative — EngineInstance equals AD_Client

**Rejected.**

One instance may host several dedicated Clients.

One tenant may also use different Clients across regional instances.

---

# 156. Rejected alternative — active-active multi-region ERP by default

**Rejected.**

The complexity is disproportionate to initial requirements and threatens accounting consistency.

---

# 157. Rejected alternative — database replication as integration

**Rejected.**

Replication solves database availability/distribution.

It does not define business interoperability.

Canonical APIs and events remain the integration mechanism.

---

# 158. Rejected alternative — DNS as the complete routing model

**Rejected.**

It lacks canonical context, binding semantics, auditability and migration history.

---

# 159. Rejected alternative — AWS resources as canonical identity

**Rejected.**

Cloud infrastructure is replaceable implementation detail.

---

# 160. Rejected alternative — Kubernetes as an architectural prerequisite

**Rejected.**

Baobab requires orchestration capability, not Kubernetes dependency.

Kubernetes may be adopted when operational scale warrants it.

---

# 161. Rejected alternative — central global logging without residency controls

**Rejected.**

Observability systems can contain sensitive tenant and financial information and must obey the same governance discipline.

---

# 162. Rejected alternative — automatic isolation downgrade

**Rejected.**

Cost optimisation cannot silently weaken security, residency or availability guarantees.

---

# 163. Non-negotiable invariants

```text
INV-ERP-ISO-001
Engine and EngineInstance are distinct.

INV-ERP-ISO-002
Tenant and EngineInstance are distinct.

INV-ERP-ISO-003
LegalEntity and EngineInstance are distinct.

INV-ERP-ISO-004
Market and DeploymentRegion are distinct.

INV-ERP-ISO-005
Infrastructure Region never defines business identity.

INV-ERP-ISO-006
Every production ERP workload has an explicit IsolationProfile.

INV-ERP-ISO-007
The strongest applicable isolation requirement prevails.

INV-ERP-ISO-008
Every production EngineInstance has an explicit deployment region.

INV-ERP-ISO-009
Every production EngineInstance has an explicit residency policy.

INV-ERP-ISO-010
ERP databases remain private to ERP.

INV-ERP-ISO-011
Shared database infrastructure never implies shared engine schemas or credentials.

INV-ERP-ISO-012
Canonical IDs survive EngineInstance migration.

INV-ERP-ISO-013
Historical EngineInstance identity is retained after retirement.

INV-ERP-ISO-014
CapabilityBinding determines authoritative runtime routing.

INV-ERP-ISO-015
Mapping existence alone does not make an EngineInstance authoritative.

INV-ERP-ISO-016
Only one authoritative ERP write path exists per resolved capability scope during ordinary operation.

INV-ERP-ISO-017
IsolationProfile changes are governed lifecycle operations.

INV-ERP-ISO-018
Automatic cost optimisation cannot reduce required isolation.

INV-ERP-ISO-019
Data residency covers backups, logs, events and replicas—not only primary databases.

INV-ERP-ISO-020
Cross-region event transport respects data classification.

INV-ERP-ISO-021
Shared instances acknowledge shared failure and upgrade domains.

INV-ERP-ISO-022
Dedicated instances may be introduced without changing canonical business identity.

INV-ERP-ISO-023
Production and non-production deployments are different EngineInstances.

INV-ERP-ISO-024
Cloud-provider identifiers are never Baobab canonical identifiers.

INV-ERP-ISO-025
ERP multi-region active-active operation requires a separate explicit ADR.

INV-ERP-ISO-026
Disaster-recovery failover preserves canonical event and mapping lineage.

INV-ERP-ISO-027
Retiring infrastructure does not erase canonical EngineInstance history.

INV-ERP-ISO-028
Desired isolation and observed deployment topology must be reconcilable.

INV-ERP-ISO-029
Infrastructure provisioning and ERP business configuration are separate responsibilities.

INV-ERP-ISO-030
No tenant may escape its resolved EngineInstance through caller-controlled routing.
```

---

# 164. Initial Baobab topology

Subject to regulatory validation, the initial cost-conscious topology SHOULD be:

```text
                         BAOBAB CONTROL PLANE
                                  │
                      CapabilityBinding Resolver
                                  │
                                  ▼
                         ERP-AF-SOUTH-01
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
               iDempiere 13                  Outbox
                    │                           │
                    ▼                           ▼
               PostgreSQL                Event Transport
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
     NABHOLD     THAMANI     ZURIBEANS
     Client      Client       Client
```

Each legal entity/tenant receives its own native Client boundary.

The infrastructure is initially shared.

The architecture is not.

---

# 165. Future topology

As Baobab grows:

```text
                        BAOBAB ERP ENGINE
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
 ERP-AF-SOUTH-01       ERP-AF-EAST-01       ERP-EU-WEST-01
          │                    │                    │
      tenants /            tenants /            tenants /
       markets              markets              markets
```

and where required:

```text
                  ERP-THAMANI-DEDICATED-01
                              │
                           THAMANI
```

Nothing above this layer needs to know that Thamani moved.

Consumers still ask:

```text
Give me the ERP capability
for:
    tenant T
    legal entity L
    market M
    context C
```

The Control Plane resolves where that capability currently lives.

---

# 166. Acceptance criteria

ADR-ERP-003 SHALL be considered implemented when:

- [ ] `EngineInstance` is a first-class Control Plane resource.
- [ ] `IsolationProfile` is a first-class Control Plane resource.
- [ ] DeploymentRegion is represented independently from Market.
- [ ] Environment is represented independently from Region.
- [ ] Every production ERP EngineInstance declares an IsolationProfile.
- [ ] Every production instance declares deployment region and residency policy.
- [ ] Shared-instance/dedicated-client deployment is supported.
- [ ] Dedicated-instance deployment is supported architecturally.
- [ ] CapabilityBinding routes to EngineInstance rather than hard-coded hosts.
- [ ] Consumer applications do not store ERP hostnames as business routing state.
- [ ] ERP databases have no public ordinary application access.
- [ ] ERP database credentials are not shared with Medusa or Payload.
- [ ] A tenant can be promoted from shared to dedicated deployment without changing canonical IDs.
- [ ] Historical EngineInstance and Mapping records survive migration.
- [ ] Split-brain write routing is prevented.
- [ ] Migration has explicit lifecycle state.
- [ ] EngineInstance has explicit lifecycle state.
- [ ] Backup and restoration procedures exist.
- [ ] Restore testing is automated or operationally scheduled.
- [ ] RPO and RTO are explicit production configuration.
- [ ] DR architecture supports active-passive recovery.
- [ ] Event outbox survives backup/recovery procedures.
- [ ] Residency policy accounts for backups and observability.
- [ ] Cross-region event flows are classification-aware.
- [ ] Shared-instance resource contention is observable.
- [ ] Isolation policy drift can be detected.
- [ ] Production and non-production are isolated.
- [ ] Infrastructure can be rebuilt reproducibly.
- [ ] Engine software/container provenance can be identified.
- [ ] EngineInstance retirement preserves historical identity.
- [ ] No AWS/Kubernetes identifier is used as canonical business identity.

---

# 167. Final architectural statement

Baobab ERP deployment SHALL therefore follow this model:

```text
                     CANONICAL BUSINESS WORLD

              Tenant ─ LegalEntity ─ Market
                         │
                         ▼
                       Context
                         │
                         ▼
                     Capability
                         │
                         ▼
                  CapabilityBinding
                         │
                         ▼
                  IsolationProfile
                         │
                         ▼

                 CONTROL PLANE RESOLUTION

                         │
                         ▼
                    EngineInstance
                         │
             ┌───────────┼───────────┐
             │           │           │
         Region      Residency    Lifecycle
             │          Policy       State
             │
             ▼

                   PHYSICAL ERP WORLD

                    iDempiere
                         │
                    PostgreSQL
                         │
                      Client
                         │
                    Organization
```

The crucial separation is:

```text
WHO?
    Tenant / LegalEntity

WHERE BUSINESS HAPPENS?
    Market

WHAT CAPABILITY?
    ERP Capability

HOW IS IT ISOLATED?
    IsolationProfile

WHERE DOES THE SOFTWARE RUN?
    EngineInstance + DeploymentRegion

HOW DOES iDEMPIERE REPRESENT IT?
    AD_Client + AD_Org
```

None of those questions SHALL be answered by pretending they are the same concept.

The governing principle is:

> **Business identity must outlive infrastructure topology.**

A tenant may begin as one Client on a shared South African instance, expand into several African markets, move one market to a regional deployment, become large enough for a dedicated ERP instance, survive a cloud-region evacuation and eventually migrate again—all while its canonical identity and external contracts remain stable.

That is the standard Baobab requires if multi-tenancy, diverse regions, markets, currencies and future scale are to be architectural properties rather than later retrofits.