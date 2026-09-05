# ADR-ERP-013 — ERP Deployment, Release, Upgrade and Configuration Management Architecture

**Status:** Accepted  
**Decision class:** ERP / Deployment / Release Engineering / Upgrade / Configuration / Supply Chain  
**Scope:** `nabhold/baobab-erp`, `nabhold/shared`, `nabhold/infrastructure`, `nabhold/baobab-dev`, `nabhold/baobab-cp`, CI/CD, container registry and production `EngineInstance`s  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-012  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL operate the iDempiere ERP Engine through a controlled, immutable, reproducible and auditable software-delivery lifecycle.

The deployable ERP runtime SHALL be treated as a composed release consisting of:

```text
Baobab ERP Release
│
├── iDempiere Platform
├── Baobab ERP Extensions
├── Approved Localisation Extensions
├── Approved Third-Party Extensions
├── Database Schema Expectations
├── Configuration Baseline
├── Runtime Dependencies
└── Deployment Manifest
```

No production `EngineInstance` SHALL be defined merely as:

```text
"an iDempiere server"
```

It SHALL have a precisely identifiable release composition.

The governing principle is:

> **Every production ERP state must be attributable to an identifiable software release, configuration baseline and controlled deployment event.**

---

# 2. Objectives

This ADR establishes how Baobab SHALL:

- build ERP artifacts;
- version releases;
- manage iDempiere upgrades;
- manage Baobab OSGi extensions;
- manage localisation packages;
- control third-party plugins;
- build production containers;
- manage configuration;
- evolve PostgreSQL;
- promote releases between environments;
- deploy shared and dedicated EngineInstances;
- detect configuration drift;
- perform roll-forward and rollback;
- preserve software provenance;
- generate SBOMs;
- scan dependencies and containers;
- enforce compatibility;
- coordinate maintenance;
- recover failed releases;
- maintain reproducibility.

---

# 3. Release versus deployment

Baobab SHALL distinguish:

```text
Release
    immutable collection of software artifacts

Deployment
    installation of a release into an environment

Configuration
    governed runtime/business settings

Migration
    transformation required to move state between versions
```

These terms SHALL NOT be used interchangeably.

---

# 4. Immutable release principle

Once published, a production release SHALL be immutable.

This is prohibited:

```text
baobab-erp:1.4.0
     │
     ├── Monday → image A
     │
     └── Friday → image B
```

The same immutable release identifier SHALL always resolve to the same artifact composition.

---

# 5. Artifact digest

Production deployment SHOULD ultimately reference immutable artifact digests rather than mutable tags alone.

Conceptually:

```text
release
   ↓
container image
   ↓
sha256:<digest>
```

Tags remain useful for human navigation.

Digests establish artifact identity.

---

# 6. Release composition

A release manifest SHALL identify at least:

```yaml
release:
  version: 1.4.0

idempiere:
  version: "<approved-version>"

extensions:
  baobab:
    - name: baobab-erp-context
      version: 1.4.0
    - name: baobab-erp-events
      version: 1.4.0

localisations:
  - name: "<approved-localisation>"
    version: "<version>"

database:
  compatibility: "<declared-range>"

contracts:
  version: "<shared-contract-version>"
```

The actual schema SHALL be defined separately.

---

# 7. Release manifest authority

The release manifest SHALL be version-controlled.

It SHALL provide machine-readable evidence of exactly what constitutes a Baobab ERP release.

---

# 8. iDempiere baseline

Baobab SHALL maintain an explicitly approved iDempiere baseline.

The ERP repository SHALL NOT implicitly consume:

```text
latest
main
master
HEAD
```

for production builds.

---

# 9. Upstream independence

Baobab SHALL track upstream iDempiere development without automatically deploying upstream changes.

The lifecycle is:

```text
Upstream Release
       │
       ▼
Compatibility Assessment
       │
       ▼
Baobab Integration Branch
       │
       ▼
Automated Validation
       │
       ▼
ERP Regression
       │
       ▼
Localisation Validation
       │
       ▼
Baobab Release
```

---

# 10. No permanent core fork

ADR-ERP-004 remains binding.

Baobab SHALL avoid maintaining a permanent divergent fork of iDempiere core.

---

# 11. Patch exception

If an urgent upstream defect requires a temporary patch, Baobab MAY maintain a controlled patch.

The patch SHALL have:

```text
reason
upstream reference
owner
introduced version
removal condition
```

---

# 12. Patch debt

Temporary upstream patches SHALL be tracked as architectural/technical debt.

They SHALL not silently become permanent.

---

# 13. Extension architecture

Baobab functionality SHALL primarily be delivered through supported extension mechanisms.

The expected extension families remain:

```text
org.nabhold.baobab.erp.contract

org.nabhold.baobab.erp.context

org.nabhold.baobab.erp.identity

org.nabhold.baobab.erp.integration

org.nabhold.baobab.erp.application

org.nabhold.baobab.erp.events

org.nabhold.baobab.erp.outbox

org.nabhold.baobab.erp.observability

org.nabhold.baobab.erp.security
```

Exact bundle decomposition MAY evolve.

---

# 14. Extension versioning

Baobab ERP extensions SHALL be versioned.

A release manifest SHALL identify the exact extension versions deployed.

---

# 15. Extension compatibility

Each extension SHALL declare compatibility with the supported iDempiere baseline.

---

# 16. Compatibility matrix

Baobab SHALL maintain a machine-readable compatibility matrix.

Conceptually:

| Component | Version | Compatible |
|---|---:|---|
| iDempiere | X | yes |
| PostgreSQL | 17 | yes |
| Baobab ERP extensions | 1.4 | yes |
| ZA localisation | X | yes |
| Shared contracts | 3.x | yes |
| Java runtime | approved version | yes |

---

# 17. Compatibility is tested

A compatibility declaration without integration tests SHALL not be sufficient for production promotion.

---

# 18. Localisation packages

Localisation packages SHALL follow ADR-ERP-009.

They SHALL be independently:

```text
identified
versioned
validated
approved
tracked
```

---

# 19. Localisation is part of release compatibility

A localisation package compatible with iDempiere release `N` SHALL NOT automatically be assumed compatible with release `N+1`.

---

# 20. Localisation certification

An ERP upgrade affecting a financially enabled Market SHALL trigger localisation compatibility validation before production promotion.

---

# 21. Third-party plugins

Third-party ERP plugins SHALL undergo controlled admission.

At minimum Baobab SHALL assess:

```text
source
maintainer
license
version
security posture
update history
iDempiere compatibility
database impact
tenant impact
financial impact
```

---

# 22. Plugin provenance

Production SHALL not install plugins from unidentified binaries.

---

# 23. Internet installation

Production ERP SHALL NOT dynamically download arbitrary plugins from the public internet.

---

# 24. Approved artifact repository

Production dependencies SHALL come through approved artifact/build mechanisms.

---

# 25. Dependency pinning

Build inputs SHOULD be pinned strongly enough to support reproducibility.

---

# 26. GitHub Actions

GitHub Actions used for Baobab ERP delivery SHALL follow organisation policy requiring actions to be pinned to full commit SHAs.

---

# 27. Workflow reuse

Organisation-wide CI/CD controls SHOULD be consumed from `nabhold/shared` where they represent common Nabhold standards.

---

# 28. Repository ownership

`nabhold/baobab-erp` owns:

```text
ERP source
ERP extension source
ERP-specific tests
ERP release definition
ERP compatibility declaration
ERP database migration logic
```

---

# 29. Shared ownership

`nabhold/shared` owns organisation-wide:

```text
contract schemas
CI policy
reusable workflows
security standards
artifact conventions
```

where applicable.

---

# 30. Infrastructure ownership

`nabhold/infrastructure` owns:

```text
production infrastructure
deployment orchestration
networking
managed databases
secret integration
observability infrastructure
backup infrastructure
```

---

# 31. Control Plane ownership

`nabhold/baobab-cp` owns canonical deployment topology metadata:

```text
Engine
EngineInstance
CapabilityBinding
IsolationProfile
Market
```

It SHALL not build ERP binaries.

---

# 32. Development environment

`nabhold/baobab-dev` SHALL provide an approved developer environment/toolbox.

It SHALL NOT become the production ERP runtime image.

---

# 33. Production image

The production ERP image SHALL be purpose-built.

It SHALL contain only the runtime components required to operate the ERP Engine.

---

# 34. Build tools

Compilers, debugging utilities and general development tooling SHOULD be excluded from final runtime images unless operationally justified.

---

# 35. Multi-stage build

Where practical, production container construction SHOULD separate:

```text
build environment
       │
       ▼
runtime environment
```

---

# 36. Reproducible builds

Given identical approved source and pinned inputs, Baobab SHOULD be capable of reproducing materially equivalent release artifacts.

---

# 37. Build provenance

Every release SHALL record:

```text
repository
commit SHA
workflow
build time
artifact digest
release version
dependency metadata
```

---

# 38. Release provenance

Operators SHALL be able to determine which source revision produced a running production artifact.

---

# 39. SBOM

Production releases SHALL generate a Software Bill of Materials.

---

# 40. SBOM contents

The SBOM SHOULD identify relevant:

```text
Java dependencies
OS packages
Baobab extensions
iDempiere components
third-party plugins
localisation packages
```

---

# 41. SBOM retention

SBOMs SHALL be retained with release evidence.

---

# 42. Vulnerability scanning

Baobab SHALL scan:

```text
source dependencies
container images
third-party components
```

using organisation-approved tooling.

---

# 43. Vulnerability is not automatic deployment failure

Vulnerability policy SHALL consider:

```text
severity
exploitability
reachability
runtime exposure
available mitigation
```

rather than treating every scanner finding identically.

---

# 44. Critical vulnerability

A materially exploitable critical vulnerability MAY block release or require emergency remediation.

---

# 45. Release signing

Production artifacts SHOULD support cryptographic signing/provenance verification as the supply-chain architecture matures.

---

# 46. Promotion principle

Baobab SHALL promote the same immutable artifact between environments.

This is preferred:

```text
Build once
   │
   ▼
Development
   │
   ▼
Test
   │
   ▼
Staging
   │
   ▼
Production
```

over:

```text
build dev image
build test image
build staging image
build production image
```

from potentially different source states.

---

# 47. Environment-specific configuration

Environment differences SHALL be injected as configuration rather than requiring different binaries.

---

# 48. Configuration taxonomy

ERP configuration SHALL be classified.

At minimum:

```text
Build Configuration

Deployment Configuration

Platform Configuration

ERP Technical Configuration

ERP Business Configuration

Financial Configuration

Localisation Configuration

Secrets
```

---

# 49. Build configuration

Build configuration controls how artifacts are produced.

Examples:

```text
Java build options
dependency versions
bundle composition
```

---

# 50. Deployment configuration

Deployment configuration includes:

```text
replica count
resource limits
network endpoints
health settings
```

---

# 51. Platform configuration

Platform configuration includes:

```text
EngineInstance identity
Control Plane endpoint
event infrastructure
observability endpoints
```

---

# 52. ERP technical configuration

ERP technical configuration includes technical runtime behaviour that is not ordinary business master data.

---

# 53. Business configuration

Business configuration includes operational ERP setup such as:

```text
document types
workflow configuration
business rules
```

where appropriate.

---

# 54. Financial configuration

Financial configuration includes:

```text
accounting schema
chart of accounts
tax rules
period configuration
costing configuration
currencies
```

and receives stronger governance.

---

# 55. Localisation configuration

Localisation configuration is jurisdiction-specific and follows ADR-ERP-009.

---

# 56. Secrets

Secrets SHALL NOT be committed into ordinary source-controlled configuration.

---

# 57. Configuration as code

Configuration suitable for declarative management SHOULD be represented as code/data under version control.

---

# 58. Not all ERP state is configuration-as-code

Baobab SHALL NOT attempt to represent every iDempiere business record in Git.

Operational business data belongs in ERP.

---

# 59. Configuration boundary

The test is:

> Can this value be deterministically promoted as governed environment/business configuration without representing an ordinary transaction or master-data lifecycle?

If yes, configuration-as-code MAY be appropriate.

---

# 60. Configuration schema

Important configuration formats SHALL have schemas where practical.

---

# 61. Configuration validation

Configuration SHALL be validated before production application.

---

# 62. Configuration version

Material configuration baselines SHALL be version-identifiable.

---

# 63. Configuration provenance

Operators SHALL be able to determine:

```text
who changed configuration
what changed
when
why
which release expected it
```

---

# 64. Configuration drift

Baobab SHALL detect material divergence between approved and deployed configuration.

---

# 65. Drift categories

Drift SHOULD be classified:

```text
benign
expected
unauthorised
dangerous
unknown
```

---

# 66. Financial drift

Unexpected drift in:

```text
accounting schema
tax rules
document numbering
period controls
currency configuration
```

SHALL receive elevated severity.

---

# 67. Drift correction

Drift SHALL not always be automatically overwritten.

For financial configuration, automated overwrite may itself be dangerous.

---

# 68. Desired versus observed state

Baobab SHALL distinguish:

```text
Desired Configuration

Observed Configuration
```

Reconciliation determines whether they agree.

---

# 69. Configuration reconciliation

Configuration reconciliation SHALL integrate with ADR-ERP-011.

---

# 70. Manual production changes

Emergency manual production configuration changes MAY occur only through controlled privileged procedures.

---

# 71. Emergency change capture

Emergency changes SHALL subsequently be:

```text
documented
audited
reconciled
incorporated into desired state
or explicitly reverted
```

---

# 72. Database ownership

The ERP database schema is owned by the ERP Engine.

Other Baobab repositories SHALL not run migrations directly against the ERP database.

---

# 73. Native schema

iDempiere-owned schema evolution SHALL follow supported upstream mechanisms.

---

# 74. Baobab schema

Baobab-specific ERP tables such as:

```text
BB_Outbox
BB_Inbox
BB_Idempotency
```

where implemented, SHALL have explicit migration ownership.

---

# 75. No arbitrary SQL startup mutation

Production application startup SHALL NOT execute uncontrolled schema mutation.

---

# 76. Migration phase

Database migrations SHALL be explicit deployment operations.

---

# 77. Migration ordering

Conceptually:

```text
Pre-deployment Validation
        │
        ▼
Backup / Recovery Point
        │
        ▼
Schema Compatibility Check
        │
        ▼
Migration
        │
        ▼
Application Deployment
        │
        ▼
Validation
```

Exact sequencing may differ for compatible expand/contract migrations.

---

# 78. Migration idempotency

Where practical, migration execution SHOULD be safely detectable/repeatable.

---

# 79. Migration ledger

Applied Baobab schema migrations SHALL be recorded.

---

# 80. Migration immutability

A migration already applied to production SHALL not be silently rewritten.

A correction SHALL use a subsequent migration.

---

# 81. Destructive migration

Destructive schema changes SHALL require explicit review.

---

# 82. Data migration

Data transformations SHALL distinguish:

```text
schema migration
data migration
business migration
```

---

# 83. Business migration

Changing business meaning cannot be hidden inside an apparently technical SQL migration.

---

# 84. Expand/contract strategy

Where zero/minimal downtime is required, Baobab SHOULD prefer compatible expand/contract migrations.

Conceptually:

```text
1. Add new representation
2. Deploy code compatible with old + new
3. Migrate/backfill
4. Switch usage
5. Verify
6. Remove old representation later
```

---

# 85. Backward compatibility

During rolling deployment, old and new application replicas may coexist.

Therefore the database/API/event schema SHALL remain compatible for the overlap period.

---

# 86. Rolling deployment suitability

Rolling deployment MAY be used for stateless ERP facade components when compatibility is proven.

---

# 87. iDempiere runtime upgrade

An iDempiere platform upgrade SHALL NOT automatically be assumed safe for rolling mixed-version operation.

---

# 88. Maintenance deployment

Where mixed-version operation is unsafe, Baobab SHALL use a controlled maintenance deployment.

---

# 89. Blue/green

Blue/green deployment MAY be used for ERP application layers where state authority remains singular and database compatibility permits it.

---

# 90. Blue/green does not duplicate financial authority

This is prohibited:

```text
BLUE ERP DB  ← writes

GREEN ERP DB ← writes
```

for the same Context during deployment.

---

# 91. Canary

Canary deployment MAY be used for stateless integration/API layers.

---

# 92. Financial canary limitation

A canary SHALL NOT split financial state across independent databases merely to test a release.

---

# 93. Shadow traffic

Read-only shadow evaluation MAY be used where sensitive data/security policy permits.

Shadow requests SHALL not create business side effects.

---

# 94. Shared EngineInstance upgrade

All AD_Clients hosted within a shared iDempiere EngineInstance normally share the same platform runtime version.

---

# 95. Shared upgrade consequence

For:

```text
ERP-AF-SOUTH-01

├── NABHOLD
├── THAMANI
└── ZURIBEANS
```

an iDempiere platform upgrade affects all hosted clients.

---

# 96. Maintenance blast radius

Shared EngineInstance economics therefore imply a shared:

```text
upgrade window
runtime version
maintenance blast radius
rollback boundary
```

---

# 97. Dedicated EngineInstance

A dedicated EngineInstance MAY adopt a different approved upgrade schedule within the supported version policy.

---

# 98. Version skew

Controlled version skew between EngineInstances MAY be allowed.

---

# 99. Unbounded version skew

Baobab SHALL NOT support arbitrary historical ERP versions indefinitely.

---

# 100. Supported-version window

The ERP architecture SHALL define an approved version-support window.

---

# 101. Contract compatibility during skew

Canonical API/event contracts SHALL permit supported EngineInstances to coexist across approved ERP versions.

This is one reason Baobab contracts SHALL remain independent from native iDempiere APIs.

---

# 102. Engine capability declaration

An EngineInstance SHOULD expose its effective:

```text
ERP release
iDempiere version
extension version
contract compatibility
localisation versions
```

to authorised management tooling.

---

# 103. Upgrade eligibility

Before upgrade, an EngineInstance SHALL pass eligibility checks.

Possible checks include:

```text
supported source version
database health
backup health
reconciliation health
no critical unresolved incidents
compatible localisation
sufficient storage
```

---

# 104. Financial close awareness

ERP upgrades SHOULD avoid sensitive financial close windows unless explicitly approved.

---

# 105. Maintenance window

Disruptive upgrades SHALL use governed maintenance windows.

---

# 106. Tenant communication

Where maintenance affects a consuming Tenant, appropriate notification SHALL occur according to service policy.

---

# 107. Drain before disruptive deployment

Before a disruptive deployment:

```text
EngineInstance
      │
      ▼
DRAINING
      │
      ▼
reject/redirect new work
      │
      ▼
complete safe in-flight work
      │
      ▼
deploy
```

where architecture permits.

---

# 108. Background process coordination

Scheduled ERP jobs SHALL be accounted for during upgrade.

---

# 109. Event publisher coordination

Outbox publishers SHALL be safely stopped/restarted without losing committed event intent.

---

# 110. Deployment lock

A mechanism SHOULD prevent concurrent incompatible deployments against the same EngineInstance.

---

# 111. Upgrade preflight

A production upgrade SHOULD verify:

```text
current release
target release
database compatibility
backup status
replication status
available storage
extension compatibility
localisation compatibility
configuration compatibility
```

---

# 112. Pre-upgrade recovery point

ADR-ERP-012 remains binding.

A suitable recovery point SHALL exist before materially destructive upgrades.

---

# 113. Upgrade execution

Conceptually:

```text
Change Approved
      │
      ▼
Preflight
      │
      ▼
Recovery Point Verified
      │
      ▼
Drain
      │
      ▼
Migrate
      │
      ▼
Deploy
      │
      ▼
Startup Validation
      │
      ▼
ERP Smoke Tests
      │
      ▼
Financial Tests
      │
      ▼
Integration Tests
      │
      ▼
Resume
      │
      ▼
Observe
      │
      ▼
Reconcile
```

---

# 114. Post-deployment smoke tests

Smoke tests SHALL verify critical runtime behaviour.

---

# 115. Business smoke tests

Production-safe business validation SHOULD include representative ERP capabilities.

---

# 116. Financial validation

Where financial behaviour changed, tests SHALL verify relevant posting/accounting behaviour.

---

# 117. Integration validation

Deployment validation SHALL include critical:

```text
Control Plane resolution
API
mapping
outbox
event publication
```

paths.

---

# 118. Localisation validation

Where a release changes localisation behaviour, jurisdiction-specific validation SHALL occur.

---

# 119. Observation window

A release SHOULD remain under elevated observation after deployment.

---

# 120. Post-release reconciliation

Material ERP releases SHOULD trigger targeted reconciliation.

---

# 121. Deployment success

A deployment SHALL not be considered successful solely because:

```text
container = running
```

---

# 122. Success criteria

Production success SHOULD include:

```text
runtime healthy
database healthy
security healthy
critical ERP operation healthy
event publication healthy
mapping healthy
reconciliation acceptable
```

---

# 123. Rollback versus roll-forward

Baobab SHALL explicitly distinguish:

```text
Rollback
    return software to prior version

Roll-forward
    deploy a corrected newer version
```

---

# 124. Roll-forward preference

After irreversible database or business-state change, roll-forward is often safer.

---

# 125. Rollback compatibility

Rollback SHALL only be offered where the previous release remains compatible with current database/configuration state.

---

# 126. No fictional rollback

A deployment pipeline SHALL NOT expose a "rollback" button if the underlying migration makes rollback unsafe.

---

# 127. Business transactions survive rollback

Transactions created by the new release SHALL not be deleted merely because application software is rolled back.

---

# 128. Schema rollback

Database downgrade SHALL be explicit.

It SHALL not be assumed possible.

---

# 129. Restore-based rollback

Restoring a pre-deployment backup is a disaster/data-recovery action.

It is NOT an ordinary application rollback once post-deployment business writes have occurred.

---

# 130. Failed deployment

A failed deployment SHALL enter a controlled state.

Conceptually:

```text
DEPLOYING
   │
   ├── success → VALIDATING
   │
   └── failure → RECOVERY_REQUIRED
```

---

# 131. Failed validation

If deployment succeeds technically but financial/integration validation fails, the EngineInstance SHALL remain restricted until disposition is determined.

---

# 132. Feature controls

Baobab MAY use feature controls to decouple deployment from capability activation.

---

# 133. Deployment versus activation

A capability MAY be:

```text
deployed
but
not activated
```

---

# 134. Feature-control ownership

Feature controls affecting tenant/financial behaviour SHALL have explicit ownership and Context.

---

# 135. Feature controls are not configuration chaos

Flags SHALL not become permanent undocumented branches of business logic.

---

# 136. Flag lifecycle

A temporary flag SHALL have:

```text
owner
purpose
introduced version
removal condition
```

---

# 137. Database-backed feature flags

If feature controls are persisted, their recovery and audit semantics SHALL be defined.

---

# 138. CapabilityBinding remains authority

A feature flag SHALL NOT replace Control Plane `CapabilityBinding` for determining which EngineInstance provides a capability.

---

# 139. Release channels

Baobab MAY define channels such as:

```text
development
candidate
stable
```

---

# 140. Production eligibility

Only approved stable releases SHALL normally be eligible for production.

---

# 141. Release candidate

A release candidate SHALL be immutable once promoted for validation.

---

# 142. Rebuild after failure

Changing source after RC validation creates a new candidate.

It SHALL not retain the previous candidate's identity.

---

# 143. Semantic versioning

Baobab SHOULD use a clear release-versioning policy.

Semantic versioning MAY be used for Baobab-owned ERP release artifacts where appropriate.

---

# 144. iDempiere version independence

Baobab ERP release version SHALL not have to equal the upstream iDempiere version.

Example:

```text
Baobab ERP 2.3.1
    └── iDempiere <approved baseline>
```

---

# 145. Contract version independence

API/event schema versions SHALL not automatically increment whenever application release version changes.

---

# 146. Database version independence

Database migration version is also a distinct dimension.

---

# 147. Version dimensions

Therefore:

```text
Baobab ERP Release Version

iDempiere Version

Baobab Extension Version

Localisation Version

Database Migration Version

API Contract Version

Event Contract Version

Configuration Baseline Version
```

are related but distinct.

---

# 148. Release metadata

Control Plane MAY record selected deployment metadata such as:

```text
release version
artifact digest
compatibility state
```

for EngineInstance management.

---

# 149. CP does not become artifact registry

Control Plane SHALL not replace the container/artifact registry.

---

# 150. Artifact registry

An approved registry SHALL be authoritative for immutable production artifacts.

---

# 151. Artifact retention

Artifacts required for supported rollback/recovery windows SHALL be retained.

---

# 152. Artifact garbage collection

Registry cleanup SHALL not remove artifacts still required for:

```text
running EngineInstances
supported rollback
DR
forensic investigation
```

---

# 153. Environment isolation

Production and non-production SHALL use isolated runtime resources appropriate to security policy.

---

# 154. Production data in lower environments

Production data SHALL NOT be copied casually into development/test environments.

---

# 155. Sanitised test data

Where realistic data is needed, sanitisation/synthetic data SHOULD be used.

---

# 156. Staging fidelity

Staging SHOULD resemble production sufficiently to expose meaningful compatibility problems.

---

# 157. Staging is not production

Staging success does not eliminate production-specific:

```text
scale
data
integration
network
regulatory
```

risks.

---

# 158. Contract testing

CI SHALL validate compatibility with organisation contracts from `nabhold/shared`.

---

# 159. Consumer contract testing

Critical consumers MAY add consumer-driven compatibility tests.

---

# 160. Contract evolution

Breaking canonical API/event changes SHALL follow their respective versioning ADRs.

A deployment SHALL not silently introduce breaking interoperability changes.

---

# 161. Database integration testing

CI SHALL test ERP migrations against a representative PostgreSQL environment.

---

# 162. Real iDempiere testing

Critical extension compatibility SHALL be tested against real supported iDempiere runtime/database behaviour.

Mocks alone are insufficient.

---

# 163. Upgrade test

Every supported upgrade path SHOULD have automated or repeatable upgrade testing.

---

# 164. Upgrade path

Baobab SHALL document whether an EngineInstance may upgrade:

```text
N → N+1
```

or whether intermediate versions are required.

---

# 165. Skipped versions

Skipping unsupported migration versions SHALL be prohibited.

---

# 166. Upgrade rehearsal

High-risk production upgrades SHOULD be rehearsed against a representative restored dataset.

---

# 167. Production-size effects

Upgrade rehearsal SHOULD consider:

```text
table size
migration duration
lock duration
index build duration
WAL generation
disk requirements
```

---

# 168. Migration timeout

Database migrations SHALL have operational timeout/lock expectations.

---

# 169. Long-running migration

Large data transformations SHOULD be designed to avoid unnecessarily blocking production.

---

# 170. Index creation

Large index operations SHALL be planned according to PostgreSQL operational characteristics and workload.

---

# 171. Data backfill

Large backfills SHOULD be resumable where practical.

---

# 172. Migration observability

Migration progress SHALL be observable for material migrations.

---

# 173. Migration failure

A partially completed migration SHALL have an explicit recovery strategy.

---

# 174. Release approval

Production releases SHALL pass defined approval gates.

---

# 175. Approval evidence

The release SHOULD record evidence including:

```text
tests
security scan
SBOM
compatibility
change summary
migration assessment
approval
```

---

# 176. Separation of duties

Where risk warrants, the individual who authors a high-risk financial change SHOULD not be the sole person approving its production deployment.

---

# 177. Emergency release

Emergency releases MAY use an expedited process.

---

# 178. Emergency does not mean uncontrolled

Emergency releases SHALL still preserve:

```text
source control
artifact identity
audit
minimum validation
post-release review
```

---

# 179. Hotfix

A production hotfix SHALL produce a new immutable release.

Operators SHALL not edit code inside running containers.

---

# 180. Mutable container prohibition

This is prohibited:

```text
kubectl exec
    ↓
edit .jar
    ↓
restart
```

as ordinary release management.

---

# 181. Runtime shell

Production shell access MAY be permitted for authorised diagnostics.

It SHALL not become a deployment mechanism.

---

# 182. Configuration secrets

Runtime secrets SHALL come from approved secret-management mechanisms.

---

# 183. Secret rotation

Secrets SHALL be rotatable independently of application release where technically appropriate.

---

# 184. Secret version compatibility

Applications SHALL tolerate controlled credential rotation.

---

# 185. Certificate rotation

Certificates SHALL support rotation without rebuilding application source.

---

# 186. Configuration reload

Dynamic configuration reload MAY be supported for safe configuration classes.

---

# 187. Restart-required configuration

Configuration requiring restart SHALL be explicitly classified.

---

# 188. Financial configuration activation

Material financial configuration SHOULD support explicit effective dates where business semantics require them.

---

# 189. Software release date is not business effective date

A tax rule deployed on 20 June MAY become legally effective on 1 July.

The architecture SHALL preserve this distinction.

---

# 190. Temporal configuration

Effective-dated configuration SHALL preserve history.

---

# 191. Historical recalculation

A new configuration version SHALL NOT automatically reinterpret historical posted transactions.

---

# 192. Market-specific rollout

A release MAY support multiple Markets while enabling new localisation functionality only for approved Markets.

---

# 193. Market activation

Market activation SHALL follow ADR-ERP-009 readiness controls.

---

# 194. Deployment does not certify localisation

Installing localisation code does not mean:

```text
Market = financially certified
```

---

# 195. Compatibility failure

If a localisation fails validation against a new ERP release, affected EngineInstances SHALL not upgrade until:

```text
localisation corrected
or
capability safely isolated
```

---

# 196. Dedicated upgrade advantage

Dedicated EngineInstances permit independent upgrade cadence for workloads blocked by jurisdiction-specific compatibility.

---

# 197. Shared upgrade constraint

A shared EngineInstance SHALL upgrade only when all hosted production clients' required localisation/configuration combinations are supported.

---

# 198. Upgrade pressure

One Tenant's desire for a new ERP feature SHALL not force unsafe upgrades upon other Tenants sharing the same instance.

---

# 199. Isolation escalation

Persistent incompatible upgrade requirements MAY justify moving a Tenant to a dedicated EngineInstance.

---

# 200. Deployment state

An EngineInstance SHOULD conceptually expose deployment state:

```text
stable
deployment_pending
draining
deploying
validating
restricted
stable
failed
```

---

# 201. Release status

A Baobab ERP release MAY have:

```text
draft
candidate
approved
deprecated
retired
revoked
```

---

# 202. Revoked release

A release MAY be revoked because of a critical:

```text
security
financial
integrity
compatibility
```

defect.

---

# 203. Revocation

Revocation SHALL prevent new deployments and trigger assessment of running EngineInstances.

---

# 204. Deprecation

Deprecation SHALL include a migration target and expected retirement horizon.

---

# 205. End-of-support

Unsupported ERP versions SHALL not remain indefinitely in production without an explicit risk exception.

---

# 206. Fleet inventory

Baobab SHALL be able to answer:

```text
Which EngineInstances are running which ERP release?
```

---

# 207. Fleet compatibility

Operations SHOULD be able to identify:

```text
outdated EngineInstances
revoked releases
incompatible localisation
configuration drift
unsupported contract versions
```

---

# 208. Upgrade waves

For multiple EngineInstances, production upgrades SHOULD occur in controlled waves.

Example:

```text
internal/non-critical
        ↓
selected production instance
        ↓
observation
        ↓
remaining fleet
```

subject to tenant/regulatory requirements.

---

# 209. Blast-radius reduction

Upgrade waves reduce the risk of fleet-wide failure.

---

# 210. Shared instance caution

A shared EngineInstance may itself represent a large blast radius and SHOULD not automatically be the first production upgrade target.

---

# 211. Dedicated pilot

A representative lower-risk dedicated instance MAY be a better production pilot where available.

---

# 212. Deployment concurrency

The platform SHOULD limit simultaneous ERP upgrades so operational teams retain recovery capacity.

---

# 213. Release freeze

Baobab MAY establish release freezes around:

```text
financial year-end
critical trading periods
regulatory deadlines
major migrations
```

---

# 214. Freeze exception

Emergency security/integrity fixes MAY override a release freeze through governed approval.

---

# 215. Change record

Material production deployments SHALL have a change record.

---

# 216. Change record contents

At minimum:

```text
release
EngineInstance
change reason
risk
migration
rollback/roll-forward plan
approver
deployment time
result
```

---

# 217. Deployment audit

Production deployment actions SHALL be auditable.

---

# 218. Human versus automation identity

Audit SHALL distinguish:

```text
approving human
executing CI/CD workload
```

---

# 219. CI/CD credentials

Deployment automation SHALL use dedicated least-privilege identities.

---

# 220. Long-lived credentials

Long-lived static deployment credentials SHOULD be avoided where workload/federated identity is available.

---

# 221. Production approval boundary

CI success SHALL not automatically imply production authorisation.

---

# 222. Protected environments

Production deployment SHOULD use environment protection/approval controls appropriate to organisational governance.

---

# 223. Branch protection

Production source branches SHALL use repository protection controls.

---

# 224. CODEOWNERS

Material ERP components SHALL have appropriate CODEOWNERS review requirements.

---

# 225. Dependency automation

Automated dependency update tooling MAY create upgrade proposals.

It SHALL NOT automatically promote arbitrary ERP dependencies into production.

---

# 226. Major dependency updates

Major runtime/database/iDempiere dependency changes require compatibility validation.

---

# 227. Release notes

Every production ERP release SHALL have release notes.

---

# 228. Release note contents

Release notes SHOULD identify:

```text
features
fixes
security changes
database changes
configuration changes
contract changes
localisation changes
known issues
upgrade instructions
```

---

# 229. Machine-readable metadata

Human release notes SHOULD be complemented by machine-readable release metadata.

---

# 230. Deployment event

A successful deployment MAY emit a control/operational event such as:

```text
erp.engine-instance.release-deployed.v1
```

---

# 231. Release event payload

Such an event MAY identify:

```text
EngineInstance
previous release
new release
artifact digest
deployment ID
timestamp
```

without containing secrets.

---

# 232. Failed deployment event

Operational events MAY similarly describe deployment failure.

These are operational/control events, not ERP business events.

---

# 233. Rollback event

Rollback SHALL be auditable and MAY emit an operational event.

---

# 234. Contract publication

OpenAPI/AsyncAPI artifacts SHALL be published/versioned independently from deployment where required.

---

# 235. Contract generation

Runtime implementation SHALL be tested against published canonical contracts.

---

# 236. Documentation version

Operational documentation SHOULD identify which ERP release(s) it applies to.

---

# 237. Runbook compatibility

A runbook written for release `N` SHALL not automatically be assumed valid for `N+5`.

---

# 238. Release observability

ADR-ERP-011 telemetry SHALL include deployment/release metadata.

---

# 239. Incident correlation

Operators SHALL be able to correlate:

```text
error-rate increase
       │
       ▼
deployment
       │
       ▼
release
       │
       ▼
commit
```

---

# 240. Release health

Baobab SHOULD maintain release-health indicators across deployed EngineInstances.

---

# 241. No environment snowflakes

Production environments SHALL not depend upon undocumented one-off manual configuration.

---

# 242. Rebuild test

Baobab SHOULD periodically prove that an EngineInstance can be reconstructed from:

```text
infrastructure definitions
release artifacts
configuration
secrets
restored state
```

rather than undocumented server history.

---

# 243. Disaster recovery linkage

ADR-ERP-012 SHALL consume release provenance from this ADR.

A database backup without compatible software artifacts is incomplete recovery preparation.

---

# 244. Configuration backup

Configuration not deterministically reconstructible from source-controlled desired state SHALL be included in backup/recovery planning.

---

# 245. Production database is not configuration source control

The fact that a setting exists in iDempiere does not eliminate the need for governed change history for material configuration.

---

# 246. Release security

The production supply chain SHALL protect against:

```text
source tampering
workflow tampering
dependency substitution
artifact replacement
credential compromise
unapproved deployment
```

---

# 247. Artifact verification

Deployment SHOULD verify expected artifact identity before execution.

---

# 248. Provenance verification

As supply-chain maturity increases, deployment SHOULD verify signed provenance before production admission.

---

# 249. Build isolation

Production release builds SHOULD execute in controlled ephemeral build environments.

---

# 250. Build secret minimisation

Build processes SHALL not receive production secrets unless strictly required.

Normally they SHOULD receive none.

---

# 251. Runtime secrets are not build arguments

Production credentials SHALL not be embedded into container layers through build arguments.

---

# 252. Container base image

Production base images SHALL be explicitly selected and version-controlled.

---

# 253. Base-image update

Base-image security updates SHALL trigger rebuild/revalidation rather than in-place package mutation of running containers.

---

# 254. Container immutability

Running ERP containers SHALL be disposable infrastructure.

Persistent ERP business state belongs in explicitly managed stateful services/storage.

---

# 255. Persistent volume

Any persistent filesystem dependency SHALL be documented and included in recovery architecture.

---

# 256. Attachments

If ERP attachments/documents are stored outside PostgreSQL, their release-independent storage and backup consistency SHALL be explicitly designed.

---

# 257. Database and object consistency

Where a business transaction references external object storage, recovery/reconciliation SHALL detect missing objects.

---

# 258. Release invariants

```text
INV-ERP-REL-001
Production releases are immutable.

INV-ERP-REL-002
A release is identifiable by exact artifact composition.

INV-ERP-REL-003
Production does not depend on mutable "latest" artifacts.

INV-ERP-REL-004
Running artifacts are traceable to source commits.

INV-ERP-REL-005
Baobab avoids a permanent iDempiere core fork.

INV-ERP-REL-006
Temporary upstream patches are explicitly tracked.

INV-ERP-REL-007
Baobab extensions declare iDempiere compatibility.

INV-ERP-REL-008
Compatibility is tested rather than merely declared.

INV-ERP-REL-009
Localisation compatibility is validated for ERP upgrades.

INV-ERP-REL-010
Unapproved third-party plugins cannot enter production.

INV-ERP-REL-011
Production does not dynamically install arbitrary internet plugins.

INV-ERP-REL-012
Production ERP uses purpose-built runtime images.

INV-ERP-REL-013
baobab-dev is not the production ERP image.

INV-ERP-REL-014
Production artifacts have provenance.

INV-ERP-REL-015
Production releases generate an SBOM.

INV-ERP-REL-016
Production artifacts undergo vulnerability assessment.

INV-ERP-REL-017
The same immutable artifact is promoted between environments.

INV-ERP-REL-018
Environment differences are configuration rather than binary mutation.

INV-ERP-REL-019
Secrets are not ordinary source-controlled configuration.

INV-ERP-REL-020
Not all ERP operational state is configuration-as-code.

INV-ERP-REL-021
Material configuration changes are auditable.

INV-ERP-REL-022
Material configuration drift is detectable.

INV-ERP-REL-023
Financial configuration drift receives elevated control.

INV-ERP-REL-024
Other repositories do not directly migrate the ERP database.

INV-ERP-REL-025
Applied production migrations are immutable historical records.

INV-ERP-REL-026
Destructive migrations receive explicit review.

INV-ERP-REL-027
Rolling deployments require overlap compatibility.

INV-ERP-REL-028
Mixed iDempiere runtime versions are not assumed safe.

INV-ERP-REL-029
Blue/green deployment never creates duplicate authoritative financial writers.

INV-ERP-REL-030
Shared EngineInstance clients share the runtime upgrade blast radius.

INV-ERP-REL-031
Controlled EngineInstance version skew may exist.

INV-ERP-REL-032
Unbounded unsupported version skew is prohibited.

INV-ERP-REL-033
Canonical contracts remain independent of native ERP versions.

INV-ERP-REL-034
Material upgrades verify an appropriate recovery point.

INV-ERP-REL-035
Deployment success requires business/integration validation where applicable.

INV-ERP-REL-036
Material ERP upgrades trigger targeted reconciliation.

INV-ERP-REL-037
Rollback is offered only when technically safe.

INV-ERP-REL-038
Application rollback never silently erases business transactions.

INV-ERP-REL-039
Database restore is not ordinary deployment rollback.

INV-ERP-REL-040
Feature flags do not replace CapabilityBinding.

INV-ERP-REL-041
Temporary feature controls have lifecycle ownership.

INV-ERP-REL-042
Release version, contract version and database version remain distinct.

INV-ERP-REL-043
Control Plane does not replace the artifact registry.

INV-ERP-REL-044
Production data is not casually copied into lower environments.

INV-ERP-REL-045
Critical extension tests exercise real iDempiere behaviour.

INV-ERP-REL-046
Unsupported upgrade paths are prohibited.

INV-ERP-REL-047
Emergency releases remain immutable and auditable.

INV-ERP-REL-048
Operators do not patch running containers as release management.

INV-ERP-REL-049
Business effective dates remain distinct from software deployment dates.

INV-ERP-REL-050
Deploying localisation code does not certify a Market.

INV-ERP-REL-051
Shared instances upgrade only when required hosted configurations are compatible.

INV-ERP-REL-052
Production deployment actions use least-privilege identities.

INV-ERP-REL-053
Every production release has release evidence.

INV-ERP-REL-054
Deployment telemetry identifies the running release.

INV-ERP-REL-055
Recovery retains compatible software artifacts.

INV-ERP-REL-056
Runtime secrets are not embedded in container images.

INV-ERP-REL-057
Running containers are treated as replaceable infrastructure.

INV-ERP-REL-058
Release automation cannot bypass tenant or financial safety controls.

INV-ERP-REL-059
Every production EngineInstance's running release is discoverable.

INV-ERP-REL-060
No production EngineInstance depends on undocumented snowflake configuration.
```

---

# 259. Reference software supply chain

```text
Developer
    │
    ▼
Pull Request
    │
    ├── compile
    ├── unit tests
    ├── contract tests
    ├── integration tests
    ├── security scan
    └── compatibility tests
    │
    ▼
Protected Merge
    │
    ▼
Controlled Build
    │
    ├── iDempiere baseline
    ├── Baobab extensions
    ├── localisation
    └── approved dependencies
    │
    ▼
Immutable Artifact
    │
    ├── image digest
    ├── SBOM
    ├── provenance
    └── release manifest
    │
    ▼
Release Candidate
    │
    ▼
Staging
    │
    ├── ERP tests
    ├── upgrade tests
    ├── financial tests
    ├── localisation tests
    └── integration tests
    │
    ▼
Production Approval
    │
    ▼
Production Deployment
    │
    ▼
Validation
    │
    ▼
Observation
    │
    ▼
Reconciliation
    │
    ▼
STABLE
```

---

# 260. Reference EngineInstance upgrade

```text
ERP-AF-SOUTH-01
Release 1.3
      │
      ▼
Upgrade Requested
      │
      ▼
Compatibility Matrix
      │
      ├── NABHOLD localisation/config ─ OK
      ├── THAMANI localisation/config ─ OK
      └── ZURIBEANS localisation/config ─ OK
      │
      ▼
Preflight
      │
      ▼
Recovery Point
      │
      ▼
Drain
      │
      ▼
Database Migration
      │
      ▼
Deploy Release 1.4
      │
      ▼
Validate
      │
      ├── Context
      ├── Accounting
      ├── Mapping
      ├── API
      ├── Outbox
      └── Localisation
      │
      ▼
Resume
      │
      ▼
Observe
      │
      ▼
Reconcile
      │
      ▼
STABLE
```

---

# 261. Failed-upgrade model

```text
Release N
    │
    ▼
Deploy N+1
    │
    ▼
Validation failure
    │
    ▼
Was DB/config changed incompatibly?
        │               │
       NO              YES
        │               │
        ▼               ▼
safe rollback?      roll-forward /
        │           controlled recovery
        ▼               │
Deploy N               ▼
        │          repair release
        ▼               │
Validate                ▼
        │           deploy N+1.1
        └───────┬───────┘
                ▼
             Validate
                │
                ▼
             Reconcile
```

The decision SHALL be based on state compatibility, not operator preference.

---

# 262. Shared versus dedicated release topology

```text
                BAOBAB ERP RELEASE CATALOGUE
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        Release 4.2    Release 4.1    Release 4.0
            │              │
            │              │
      ┌─────┴─────┐        │
      ▼           ▼        ▼
ERP-AF-01     ERP-UG-01   ERP-REG-01
shared        dedicated   regulated
instance      instance    instance
```

Controlled version skew is therefore possible without creating different canonical ERP contracts for each Tenant.

---

# 263. Configuration model

```text
                       SOURCE CONTROL
                            │
                 Approved Desired State
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
      Deployment       Technical        Localisation
      Configuration    Configuration    Configuration
           │                │                │
           └────────────────┼────────────────┘
                            ▼
                      EngineInstance
                            │
                            ▼
                      Observed State
                            │
                            ▼
                    Reconciliation
                       │         │
                     MATCH     DRIFT
                                 │
                                 ▼
                       classify / approve /
                       correct / investigate
```

Financial configuration receives additional governance rather than blind automatic reconciliation.

---

# 264. Release decision hierarchy

When deciding whether an ERP release is production-ready, Baobab SHALL evaluate in this order:

```text
1. Source integrity

2. Build reproducibility

3. Dependency provenance

4. Security

5. iDempiere compatibility

6. Database compatibility

7. Baobab extension compatibility

8. Canonical contract compatibility

9. Localisation compatibility

10. Financial correctness

11. Tenant isolation

12. Operational recoverability

13. Deployment readiness

14. Post-deployment reconciliation
```

---

# 265. Definition of done

ADR-ERP-013 SHALL be considered implemented when:

- [ ] A Baobab ERP release format exists.
- [ ] Release manifests are machine-readable.
- [ ] iDempiere baseline is explicitly pinned.
- [ ] Baobab extensions are versioned.
- [ ] Compatibility matrix exists.
- [ ] Localisation compatibility is represented.
- [ ] Third-party plugin admission policy exists.
- [ ] Production builds use controlled dependencies.
- [ ] GitHub Actions are SHA-pinned.
- [ ] Production image is separate from `baobab-dev`.
- [ ] Production image is purpose-built.
- [ ] Build provenance is captured.
- [ ] Container digest is captured.
- [ ] SBOM is generated.
- [ ] Dependency scanning exists.
- [ ] Container scanning exists.
- [ ] Immutable artifact promotion exists.
- [ ] Configuration taxonomy is implemented.
- [ ] Secrets are externalised.
- [ ] Material configuration is version-identifiable.
- [ ] Configuration drift detection exists.
- [ ] Financial configuration receives stronger controls.
- [ ] ERP database migration ownership is explicit.
- [ ] Baobab migration ledger exists where required.
- [ ] Migration compatibility testing exists.
- [ ] Destructive migration review exists.
- [ ] Expand/contract patterns are supported where required.
- [ ] Shared-instance upgrade policy exists.
- [ ] Dedicated-instance upgrade policy exists.
- [ ] Supported version-skew policy exists.
- [ ] Unsupported-version policy exists.
- [ ] EngineInstance release inventory exists.
- [ ] Upgrade preflight exists.
- [ ] Recovery point is verified before high-risk migration.
- [ ] Draining procedure exists.
- [ ] Background process coordination exists.
- [ ] Outbox publisher restart is safe.
- [ ] Post-deployment smoke tests exist.
- [ ] Financial validation exists where required.
- [ ] Integration validation exists.
- [ ] Localisation validation exists.
- [ ] Observation window exists.
- [ ] Post-upgrade reconciliation exists.
- [ ] Rollback safety is explicitly assessed.
- [ ] Roll-forward procedures exist.
- [ ] Feature-control lifecycle exists.
- [ ] Release approval gates exist.
- [ ] Emergency-release process exists.
- [ ] Running-container mutation is prohibited.
- [ ] Release notes exist.
- [ ] Deployment audit exists.
- [ ] Deployment uses least-privilege identities.
- [ ] Release metadata appears in observability.
- [ ] Compatible artifacts are retained for DR.
- [ ] EngineInstance rebuild can be demonstrated without undocumented state.

---

# 266. Final architectural position

Baobab SHALL reject the operating model:

```text
Download iDempiere
       │
       ▼
Install plugins
       │
       ▼
Configure server manually
       │
       ▼
Patch production
       │
       ▼
Hope upgrades work
```

The production model SHALL instead be:

```text
Approved Upstream
       │
       ▼
Pinned Baseline
       │
       ▼
Baobab Extensions
       │
       ▼
Approved Localisations
       │
       ▼
Compatibility Validation
       │
       ▼
Immutable Build
       │
       ├── Digest
       ├── SBOM
       ├── Provenance
       └── Release Manifest
       │
       ▼
Controlled Promotion
       │
       ▼
EngineInstance Preflight
       │
       ▼
Recovery Point
       │
       ▼
Deployment
       │
       ▼
Business Validation
       │
       ▼
Observation
       │
       ▼
Reconciliation
       │
       ▼
Stable Production
```

The definitive rule is:

> **Baobab does not deploy an ERP server; it promotes a known, immutable and tested ERP release into a governed EngineInstance.**

And:

> **An upgrade is complete only when software, database, configuration, localisation, canonical integration, financial behaviour and operational recoverability have all been shown to remain compatible.**

This allows iDempiere itself to evolve without making Baobab's canonical platform architecture dependent upon any particular upstream release.