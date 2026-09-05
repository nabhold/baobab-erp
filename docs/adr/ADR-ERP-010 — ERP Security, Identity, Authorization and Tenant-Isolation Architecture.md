# ADR-ERP-010 — ERP Security, Identity, Authorization and Tenant-Isolation Architecture

**Status:** Accepted  
**Decision class:** ERP / Security / Identity / Authorization / Tenant Isolation / Zero Trust  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, infrastructure/gateway components, consuming Baobab engines and Digital Estates  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-009  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL implement defence-in-depth security based on explicit identity, trusted Context resolution, capability authorization, ERP-native authorization and infrastructure isolation.

The security chain SHALL conceptually be:

```text
Identity
   ↓
Authentication
   ↓
Trusted Principal
   ↓
Baobab Context
   ↓
Capability Authorization
   ↓
EngineInstance Resolution
   ↓
Canonical Mapping
   ↓
ERP Client / Organization Context
   ↓
iDempiere Role Authorization
   ↓
Application-Service Authorization
   ↓
ERP Business Operation
```

No single layer SHALL be considered sufficient by itself.

---

# 2. Governing principle

The governing rule is:

> **Identity establishes who or what is calling; Context establishes on whose behalf and within which boundary the call occurs; authorization establishes what that principal may do in that Context.**

Therefore:

```text
Identity != Tenant
Identity != Role
Tenant != Role
Market != Role
AD_Client != Principal
AD_Org != Principal
API credential != authorization
```

---

# 3. Security boundary

The ERP Engine SHALL be treated as a protected enterprise system.

It SHALL NOT be directly exposed to arbitrary public Internet consumers.

Normal flow:

```text
External / Internal Consumer
          │
          ▼
   Trusted Edge / Gateway
          │
          ▼
Authentication / Policy
          │
          ▼
      ERP API
          │
          ▼
Context + Authorization
          │
          ▼
      iDempiere
```

---

# 4. Zero-trust posture

Network location SHALL NOT automatically establish trust.

Requests originating from:

```text
internal subnet
Kubernetes cluster
Codespace
VPN
another Baobab engine
```

still require appropriate identity and authorization.

---

# 5. Principal

Baobab SHALL distinguish principal types.

At minimum:

```text
HumanPrincipal
ServicePrincipal
WorkloadPrincipal
AutomationPrincipal
PrivilegedPrincipal
```

may exist.

These are security identities, not business organisations.

---

# 6. Human identity

Human users SHALL authenticate through the approved Baobab identity architecture before accessing ERP capabilities.

ERP-specific local accounts MAY remain necessary for administrative/back-office use.

They SHALL not become the primary identity architecture for all Baobab Digital Estates.

---

# 7. Machine identity

Every machine-to-machine ERP integration SHALL use a dedicated machine identity.

Examples:

```text
Trade Engine
Control Plane
regulatory adapter
reconciliation worker
financial export worker
approved automation
```

---

# 8. No shared machine credential

Multiple engines SHALL NOT share one generic credential such as:

```text
baobab-integration-user
```

for convenience.

Each workload SHALL be independently identifiable.

---

# 9. Workload identity

Where infrastructure supports workload identity, Baobab SHOULD prefer short-lived workload credentials over long-lived static secrets.

---

# 10. Human credentials

Human passwords SHALL NOT be embedded in:

```text
source code
container images
environment templates
GitHub repositories
CI workflows
API requests
integration scripts
```

---

# 11. Authentication versus authorization

Successful authentication answers:

> Who are you?

It does not answer:

> Are you permitted to post this supplier invoice for this legal entity?

Authorization SHALL always be evaluated separately.

---

# 12. Context

Every tenant-sensitive ERP operation SHALL execute within a resolved Baobab `Context`.

Context SHALL include or resolve sufficient information to establish:

```text
Tenant
LegalEntity where applicable
Market where applicable
DigitalEstate where applicable
Capability
Engine
EngineInstance
IsolationProfile
```

and other policy dimensions where required.

---

# 13. Context is trusted infrastructure data

Caller-provided context hints SHALL NOT become authoritative merely because they appear in an HTTP header.

For example:

```http
Baobab-Tenant-Id: <uuid>
```

does not by itself prove authorization for that Tenant.

---

# 14. Context resolution

The server SHALL derive/validate Context through trusted identity and Control Plane relationships.

Conceptually:

```text
Authenticated Principal
        │
        ▼
Principal Grants
        │
        ▼
Requested Capability
        │
        ▼
Context Resolver
        │
        ├── Tenant
        ├── LegalEntity
        ├── Market
        ├── DigitalEstate
        └── Capability
        │
        ▼
CapabilityBinding
        │
        ▼
EngineInstance
```

---

# 15. Fail closed

If Context cannot be unambiguously resolved, the request SHALL fail.

Baobab SHALL NOT guess a default Tenant for a security-sensitive ERP operation.

---

# 16. Tenant selection

A principal MAY be authorised for multiple Tenants.

Tenant selection SHALL therefore be:

```text
explicit
validated
auditable
```

rather than implicitly inferred from whichever ERP Client happens to be active.

---

# 17. LegalEntity selection

Where a Tenant contains multiple legal entities, authorization SHALL independently determine which LegalEntity the principal may act for.

---

# 18. Market selection

Market authorization SHALL be separately enforceable where business policy requires it.

Possession of Tenant access SHALL not automatically imply permission across every Market.

---

# 19. Digital Estate context

A Digital Estate SHALL only receive the capabilities assigned to it.

A public storefront SHALL not acquire unrestricted ERP finance capability because its parent LegalEntity owns the ERP Client.

---

# 20. Capability authorization

Authorization SHALL be capability-oriented.

Examples:

```text
erp.business-partners.read
erp.purchase-orders.read
erp.purchase-orders.create
erp.purchase-orders.complete
erp.goods-receipts.create
erp.goods-receipts.complete
erp.supplier-invoices.read
erp.supplier-invoices.create
erp.supplier-invoices.post
erp.payments.read
erp.payments.create
erp.payments.complete
erp.accounting-periods.read
erp.accounting-periods.manage
```

---

# 21. Capability granularity

Capabilities SHALL be granular enough to enforce meaningful separation of duties.

This is too broad:

```text
erp.admin
```

for ordinary integrations.

---

# 22. CapabilityBinding is not user authorization

`CapabilityBinding` determines where a capability is supplied.

It SHALL NOT replace principal authorization.

Conceptually:

```text
PrincipalGrant
    answers
    "may this caller use ERP purchasing?"

CapabilityBinding
    answers
    "which ERP instance supplies ERP purchasing here?"
```

Both must succeed.

---

# 23. Authorization decision

An ERP authorization decision SHOULD conceptually evaluate:

```text
principal
action
resource
Tenant
LegalEntity
Market
Capability
resource state
business policy
```

as applicable.

---

# 24. Resource authorization

Permission to access one supplier invoice SHALL NOT imply permission to access every supplier invoice in the same EngineInstance.

---

# 25. Native ERP security

iDempiere's native:

```text
AD_Client
AD_Org
AD_User
AD_Role
role access
organization access
document access
process access
```

SHALL remain part of ERP defence in depth.

Baobab SHALL not disable native security merely because an API gateway exists.

---

# 26. Canonical authorization versus native authorization

Baobab authorization and iDempiere authorization solve related but different problems.

```text
Baobab:
    platform identity
    tenant Context
    capability policy
    engine routing

iDempiere:
    ERP role
    client/org access
    document/process permissions
    native business security
```

Both SHALL be preserved.

---

# 27. AD_Client boundary

As established in ADR-ERP-002, `AD_Client` is the strongest ordinary iDempiere application tenant boundary.

Requests resolved to one Baobab Tenant SHALL never be allowed to arbitrarily change:

```text
AD_Client_ID
```

to another Client.

---

# 28. No caller-controlled AD_Client_ID

Canonical APIs SHALL NOT accept native Client selection as authorization input.

This SHALL be prohibited:

```json
{
  "ad_client_id": 1000001
}
```

as a mechanism for selecting business ownership.

---

# 29. AD_Client resolution

Native Client SHALL be resolved server-side from:

```text
Context
    ↓
CapabilityBinding
    ↓
EngineInstance
    ↓
Mapping
    ↓
AD_Client
```

---

# 30. AD_Org boundary

`AD_Org` SHALL be resolved according to approved organisational mappings and business policy.

Caller-provided `AD_Org_ID` SHALL not override canonical Context.

---

# 31. Cross-Client access

Cross-Client business access SHALL be denied by default.

Administrative exceptions require explicit privileged authorization.

---

# 32. System Client

iDempiere System Client access SHALL never be used as ordinary business integration context.

---

# 33. System Administrator

System-level administrative identities SHALL be treated as highly privileged infrastructure identities.

They SHALL not be used by:

```text
Trade Engine
Digital Estates
ordinary workers
routine ERP API integrations
```

---

# 34. Service identities inside iDempiere

Where Baobab integration requires native iDempiere users, service identities SHALL be dedicated and least privileged.

---

# 35. Service identity strategy

A service identity MAY be scoped by:

```text
EngineInstance
AD_Client
integration
capability
```

depending on security requirements.

---

# 36. Avoid universal ERP service account

A single native iDempiere service account spanning every Client SHALL be avoided.

---

# 37. Role design

iDempiere roles SHALL align with business capability boundaries rather than convenience.

Examples MAY include:

```text
Baobab ERP Purchasing Integration
Baobab ERP Sales Integration
Baobab ERP Payment Integration
Baobab ERP Reconciliation
Baobab ERP Read-Only Reporting
```

---

# 38. Role mapping

Baobab capability scopes SHALL NOT be assumed to map 1:1 to iDempiere Roles.

An explicit mapping/policy layer SHALL determine appropriate native permissions.

---

# 39. Role explosion

Baobab SHALL avoid generating thousands of native roles merely to reproduce every possible canonical Context combination.

Native roles and canonical policy SHALL remain layered.

---

# 40. Least privilege

Every principal SHALL receive only the capabilities required to perform its intended function.

---

# 41. Deny by default

New APIs, processes and integrations SHALL default to inaccessible until explicitly authorised.

---

# 42. Separation of duties

Financially sensitive workflows SHOULD enforce separation of duties where business policy requires it.

Examples:

```text
supplier creation
invoice creation
invoice approval
payment creation
payment approval
period reopening
journal posting
```

---

# 43. Machine separation of duties

Automation does not eliminate separation-of-duties requirements.

Two automated capabilities MAY require distinct machine identities and grants.

---

# 44. Privilege escalation

A process SHALL NOT acquire broader privileges simply because a downstream operation is difficult to implement with least privilege.

---

# 45. Privileged access

Privileged ERP access SHALL be explicitly classified.

Examples:

```text
platform administrator
ERP administrator
database administrator
security administrator
financial superuser
```

---

# 46. Privileged identities

Privileged identities SHALL be separate from ordinary user identities where practical.

---

# 47. Standing privilege

Permanent standing administrative privilege SHOULD be minimised.

Where infrastructure permits, temporary elevation SHOULD be preferred.

---

# 48. Break-glass access

Baobab SHALL define break-glass access for emergencies.

Break-glass SHALL be:

```text
rare
explicit
time-limited where possible
strongly authenticated
audited
alerted
reviewed afterward
```

---

# 49. Break-glass does not erase boundaries

Emergency access SHALL not disable audit.

---

# 50. Break-glass event

Security monitoring SHOULD produce an immediate privileged-access signal whenever break-glass access is used.

---

# 51. Impersonation

Administrative impersonation of another user SHALL be disabled unless an explicit support/security requirement justifies it.

If supported, it SHALL record:

```text
actual principal
impersonated principal
reason
start time
end time
operations
```

---

# 52. Delegation

Delegated authority SHALL be explicit.

Examples:

```text
manager acting for employee
finance shared service acting for subsidiary
group administrator acting for operating company
```

Ownership hierarchy alone SHALL not imply delegation.

---

# 53. Group holding company

A parent company's ownership of a subsidiary SHALL NOT automatically grant all parent users access to subsidiary ERP data.

---

# 54. Group services

Where Nabhold provides shared finance or administration services, access SHALL be represented as explicit cross-entity grants.

---

# 55. Tenant isolation

Tenant isolation SHALL be enforced at multiple layers:

```text
authentication
authorization
Context
CapabilityBinding
mapping
ERP Client
native role
database semantics
network
observability
event routing
```

---

# 56. IsolationProfile

`IsolationProfile` SHALL determine required infrastructure and application isolation.

Security enforcement SHALL honour the active profile.

---

# 57. Shared EngineInstance

In a shared instance:

```text
Tenant A → AD_Client A
Tenant B → AD_Client B
Tenant C → AD_Client C
```

is the preferred default model.

---

# 58. Cross-tenant query prevention

All canonical ERP query services SHALL establish tenant/client scope before accessing native records.

---

# 59. Query filtering is not sufficient alone

Security SHALL not rely solely on developers remembering to append:

```sql
WHERE AD_Client_ID = ?
```

to every query.

Native ERP access controls and service-layer Context SHALL provide additional protection.

---

# 60. Native query restrictions

Baobab API implementations SHALL prefer supported iDempiere model/query mechanisms that preserve client/organization context.

Raw SQL SHALL be exceptional and security-reviewed.

---

# 61. Cross-tenant object reference

Suppose Tenant A sends a canonical UUID belonging to Tenant B.

The system SHALL NOT merely retrieve the object and proceed.

It SHALL validate that the reference is authorised in the current Context.

---

# 62. IDOR prevention

Canonical UUIDs SHALL not be considered authorization secrets.

Possession or discovery of an identifier does not grant access.

---

# 63. Mapping security

ExternalReference and Mapping resolution SHALL be Context-scoped.

A mapping from another Tenant SHALL not resolve merely because the canonical UUID is valid.

---

# 64. Mapping enumeration

Mapping APIs SHALL not expose unrestricted cross-tenant mapping enumeration to ordinary consumers.

---

# 65. Native ID exposure

Native iDempiere identifiers SHOULD not appear in external contracts.

This reduces coupling and unnecessary information disclosure.

---

# 66. Database isolation

ERP PostgreSQL SHALL not be directly reachable from Digital Estates or peer engines.

---

# 67. Database credentials

Database credentials SHALL be restricted to authorised ERP runtime/operations components.

---

# 68. No shared database credential across engines

Trade, Payload and Control Plane SHALL NOT use ERP database credentials.

---

# 69. Database administration

DBA access SHALL be privileged and audited.

---

# 70. Database superuser

Application runtime SHALL not normally operate as PostgreSQL superuser.

---

# 71. Schema ownership

Runtime roles SHOULD have only the database privileges necessary for their workload.

Migration/administrative roles MAY be separate from runtime roles.

---

# 72. Migration credentials

Production schema migration credentials SHALL not be embedded in normal ERP application runtime where avoidable.

---

# 73. Network segmentation

ERP infrastructure SHALL enforce network boundaries.

Conceptually:

```text
Internet
   │
   ▼
Edge
   │
   ▼
API Gateway
   │
   ▼
ERP Application Network
   │
   ▼
ERP Database Network
```

---

# 74. Database public exposure

ERP PostgreSQL SHALL NOT be publicly Internet-accessible.

---

# 75. Administrative interfaces

ERP administrative interfaces SHOULD have stronger network/access controls than ordinary integration APIs.

---

# 76. Native iDempiere WebUI

If exposed for back-office users, native iDempiere WebUI SHALL use controlled ingress, strong authentication and appropriate session security.

It SHALL not be treated as a public Digital Estate.

---

# 77. Internal APIs

An API being labelled:

```text
internal
```

does not remove authentication requirements.

---

# 78. Service-to-service transport

Production service-to-service traffic SHALL use encrypted transport.

---

# 79. TLS

TLS SHALL be required for production API and event transport where supported by the transport architecture.

---

# 80. Mutual authentication

mTLS MAY be used for service-to-service authentication where infrastructure policy requires it.

mTLS SHALL complement, not replace, application-level authorization.

---

# 81. Gateway identity

The ERP service SHALL know whether it is trusting:

```text
end-user identity
gateway identity
delegated user identity
workload identity
```

and SHALL not confuse them.

---

# 82. Identity propagation

When a gateway acts on behalf of a human principal, the system SHOULD preserve both:

```text
original principal
immediate calling workload
```

for audit.

---

# 83. Trusted proxy

Identity headers from untrusted networks SHALL be discarded or overwritten.

Only approved gateways may supply trusted identity assertions.

---

# 84. Signed Context assertion

Baobab MAY introduce a signed, short-lived Context assertion.

Such an assertion SHOULD bind:

```text
principal
Tenant
LegalEntity
Market
Capability
audience
issuer
issued-at
expiry
request/correlation context
```

as appropriate.

---

# 85. Context assertion is not long-lived credential

Context assertions SHALL be short-lived and audience-restricted.

---

# 86. Replay resistance

Authentication/context tokens SHALL use appropriate mechanisms to limit replay risk.

---

# 87. Audience restriction

A token intended for:

```text
Trade Engine
```

SHALL not automatically be accepted by:

```text
ERP Engine
```

unless explicitly designed for that audience.

---

# 88. Token validation

ERP SHALL validate applicable:

```text
signature
issuer
audience
expiry
not-before
algorithm/policy
```

before accepting a security token.

---

# 89. Algorithm confusion

Token verification SHALL not trust arbitrary algorithms supplied by the token itself without server-side policy.

---

# 90. Clock skew

Authentication infrastructure SHALL define bounded clock-skew tolerance.

---

# 91. Session security

Human ERP sessions SHALL have:

```text
secure cookies where applicable
session expiry
idle timeout
logout/revocation
CSRF protection where applicable
```

according to the interface architecture.

---

# 92. Long-lived sessions

Privileged ERP sessions SHOULD have stricter lifetime requirements than low-risk ordinary sessions.

---

# 93. MFA

Privileged human access SHOULD require strong multi-factor authentication.

Financially sensitive roles SHOULD use MFA according to risk policy.

---

# 94. Password policy

Where local ERP passwords remain necessary, they SHALL follow approved credential policy.

---

# 95. Password storage

Baobab SHALL rely on approved identity/iDempiere mechanisms for password storage.

Plaintext/reversible application-managed password storage is prohibited.

---

# 96. Secret

A Secret includes items such as:

```text
database password
API client secret
private key
regulatory credential
webhook signing key
encryption key
```

---

# 97. Secret storage

Production secrets SHALL be stored in approved secrets-management infrastructure.

---

# 98. Secret source control

Production secrets SHALL never be committed to:

```text
Git
Dockerfile
compose files
example env files
documentation
CI workflow source
```

---

# 99. Environment examples

`.env.example` MAY contain:

```text
VARIABLE_NAME=
```

but SHALL NOT contain production secret values.

---

# 100. Secret rotation

Secrets SHALL support rotation without requiring architecture redesign.

---

# 101. Credential lifecycle

Credential lifecycle SHALL include:

```text
creation
distribution
activation
rotation
revocation
expiry
audit
```

---

# 102. Rotation without downtime

Critical machine credentials SHOULD support overlapping rotation where technically possible.

---

# 103. Certificates

Certificates SHALL have managed:

```text
issuance
storage
expiry
renewal
revocation
monitoring
```

---

# 104. Encryption at rest

ERP data SHALL use infrastructure-level encryption at rest according to Baobab production security policy.

---

# 105. Field-level protection

Highly sensitive fields MAY require additional:

```text
encryption
tokenisation
masking
```

where threat model or regulation requires.

---

# 106. Encryption is not authorization

Encrypted data SHALL still require access control after decryption.

---

# 107. Key management

Encryption keys SHALL be separated from encrypted application data.

---

# 108. Key access

Application components SHALL receive only the key capabilities they require.

---

# 109. Key rotation

Key rotation SHALL be supported according to the selected key-management architecture.

---

# 110. Sensitive data

ERP data classification SHALL identify sensitive classes including:

```text
financial records
bank accounts
tax identifiers
commercial terms
supplier information
customer information
personal data
credentials
```

---

# 111. Data minimisation

APIs and events SHALL expose only the data necessary for the consuming capability.

---

# 112. Event security

Canonical events SHALL be published only by authorised producers.

Consumers SHALL receive only event families they are authorised to consume.

---

# 113. Event broker ACL

Event infrastructure SHALL enforce producer/consumer ACLs.

---

# 114. Wildcard event consumption

Ordinary workloads SHALL NOT receive unrestricted wildcard access to all ERP events.

---

# 115. Event Tenant context

Tenant-sensitive events SHALL carry trusted canonical Context sufficient for secure routing and processing.

---

# 116. Event payload trust

Consumers SHALL validate event origin and schema before processing.

---

# 117. Event identity is not authorization

Receiving an event about an entity SHALL not automatically grant API access to that entity.

---

# 118. Cross-region event security

Cross-region event routing SHALL enforce:

```text
ResidencyPolicy
classification
producer identity
consumer authorization
```

---

# 119. DLQ security

Dead-letter queues SHALL receive the same security and residency consideration as normal event channels.

---

# 120. Replay security

Event replay SHALL be privileged.

Unrestricted replay can recreate:

```text
financial operations
notifications
downstream side effects
```

if consumers are poorly designed.

---

# 121. Consumer idempotency

Consumers SHALL remain idempotent so duplicate or replayed events do not duplicate financial effects.

---

# 122. Webhooks

Where webhooks are used, they SHALL use appropriate authenticity mechanisms such as signed requests and replay protection.

---

# 123. Webhook secrets

Webhook signing secrets SHALL be independently rotatable.

---

# 124. Webhook SSRF protection

Webhook destination management SHALL protect against server-side request forgery.

---

# 125. Outbound network policy

ERP SHALL not have unrestricted outbound Internet access merely because one regulatory adapter requires Internet connectivity.

---

# 126. Egress allowlisting

Sensitive deployments SHOULD restrict outbound traffic to approved destinations.

---

# 127. File import security

ERP file imports SHALL validate:

```text
file type
size
content
authorization
tenant context
```

before processing.

---

# 128. Spreadsheet/CSV imports

Bulk import does not bypass ordinary authorization and validation.

---

# 129. Attachment security

ERP attachments SHALL be:

```text
access-controlled
tenant-scoped
malware-scanned where appropriate
size-limited
content-type validated
```

---

# 130. Object storage

If ERP attachments use external object storage, access SHALL use scoped credentials or signed access mechanisms.

---

# 131. Object key security

Object-store paths SHALL not be treated as authorization boundaries by themselves.

---

# 132. Logs

Logs SHALL contain enough Context for security investigation without leaking sensitive payloads.

---

# 133. Security audit fields

Security-relevant logs SHOULD preserve:

```text
timestamp
principal
workload
Tenant
LegalEntity where applicable
EngineInstance
operation
resource canonical ID
authorization outcome
correlation ID
source metadata
```

---

# 134. Authentication failure logging

Repeated authentication failures SHALL be observable.

---

# 135. Authorization denial logging

High-risk authorization denials SHOULD be observable without producing excessive sensitive logs.

---

# 136. Cross-tenant denial

Attempts to access another Tenant's resources SHOULD produce security telemetry suitable for investigation.

---

# 137. Sensitive logging

Logs SHALL NOT routinely contain:

```text
passwords
tokens
private keys
full bank account details
unnecessary tax identifiers
payment credentials
```

---

# 138. Token logging

Bearer tokens SHALL never be written to normal application logs.

---

# 139. Query-string secrets

Secrets SHALL not be placed in URLs/query strings.

---

# 140. Error handling

External API errors SHALL not expose:

```text
SQL
stack traces
filesystem paths
internal credentials
native database topology
```

---

# 141. Problem Details

Canonical API errors SHALL follow ADR-ERP-005's Problem Details architecture.

Security failures SHOULD expose only enough information for legitimate clients to respond correctly.

---

# 142. Enumeration resistance

Authentication and resource errors SHOULD avoid unnecessary information that allows attackers to enumerate:

```text
users
Tenants
suppliers
invoices
native ERP IDs
```

---

# 143. Rate limiting

Security-sensitive endpoints SHALL support rate limiting.

---

# 144. Login throttling

Human authentication interfaces SHOULD have protection against automated credential attacks.

---

# 145. API abuse

Gateway/application controls SHOULD detect:

```text
excessive requests
credential misuse
unexpected tenant switching
unusual privileged operations
```

---

# 146. Denial-of-service containment

One Tenant SHALL not be able to exhaust shared ERP resources without operational safeguards.

---

# 147. Resource quotas

Shared instances MAY enforce:

```text
request limits
job limits
bulk-operation limits
attachment limits
```

where necessary.

---

# 148. Bulk operation security

Bulk APIs SHALL validate every affected object against the authorised Context.

---

# 149. Background jobs

A background job SHALL capture immutable trusted Context when created.

---

# 150. Worker Context

Workers SHALL NOT infer Tenant from mutable global process state.

---

# 151. Thread-local/global context

Context SHALL not leak between concurrent requests, threads or jobs.

---

# 152. Async isolation test

Security testing SHALL explicitly verify that:

```text
Request A / Tenant A
```

cannot contaminate:

```text
Request B / Tenant B
```

through reused threads, sessions, caches or workers.

---

# 153. Cache security

Tenant-sensitive cache keys SHALL include sufficient Context to prevent cross-tenant cache poisoning or disclosure.

---

# 154. Shared cache

A shared Redis/cache deployment SHALL not imply shared logical cache namespace.

---

# 155. Cache authorization

Cached data SHALL not bypass current authorization checks where permissions may have changed.

---

# 156. Search index security

If ERP data is projected into OpenSearch or another search system, tenant isolation SHALL be preserved there independently.

---

# 157. Analytical projection security

Financial projections SHALL retain applicable:

```text
Tenant
LegalEntity
classification
residency
```

metadata.

---

# 158. Backup security

Backups SHALL be encrypted and access-controlled.

---

# 159. Backup isolation

A backup containing multiple Tenants SHALL be classified according to the strongest applicable security requirement.

---

# 160. Restore authorization

Production restore operations SHALL be privileged and audited.

---

# 161. Restore isolation validation

After restoration, Baobab SHALL verify tenant mappings and isolation before normal service resumes.

---

# 162. Non-production data

Production ERP data SHALL not be copied into development environments without approved controls.

---

# 163. Test-data sanitisation

Where production-derived data is necessary, it SHALL be:

```text
minimised
masked
tokenised
anonymised
```

as appropriate.

---

# 164. Codespaces

GitHub Codespaces SHALL be treated as development infrastructure, not a privileged production administration environment by default.

---

# 165. Development credentials

Codespaces SHALL use development/test credentials unless explicitly approved otherwise.

---

# 166. DevContainer

The Baobab DevContainer SHALL not contain embedded production ERP credentials.

---

# 167. CI/CD identity

GitHub Actions SHALL use dedicated deployment identities with least privilege.

---

# 168. Long-lived cloud secrets in CI

Long-lived cloud credentials SHOULD be avoided where workload identity/federation is available.

---

# 169. Workflow permissions

GitHub Actions workflows SHALL declare minimum required permissions.

---

# 170. SHA pinning

Third-party GitHub Actions SHALL remain pinned according to Baobab's supply-chain policy.

---

# 171. Protected environments

Production deployment SHOULD use protected deployment environments and approval controls according to organisational policy.

---

# 172. Build provenance

Production ERP artifacts SHOULD have traceable:

```text
source commit
build workflow
dependency versions
image digest
SBOM
signature/provenance
```

---

# 173. Image security

Production ERP images SHALL be scanned for known vulnerabilities before release according to Baobab policy.

---

# 174. Base image

Runtime images SHALL use minimal supported bases appropriate for iDempiere rather than the broad development toolbox image.

---

# 175. Dependency security

ERP extensions and localisation plugins SHALL participate in dependency/security scanning.

---

# 176. Plugin supply chain

A plugin SHALL not be installed in production merely because it appears in an online repository.

---

# 177. Plugin approval

Production plugins SHALL have:

```text
source provenance
version
license
security review
compatibility validation
checksum/digest
```

---

# 178. Runtime plugin installation

Uncontrolled runtime installation of arbitrary plugins SHALL be disabled or operationally prohibited in production.

---

# 179. Reproducibility

Production ERP installations SHALL be reproducible from approved artifact/configuration definitions.

---

# 180. Vulnerability management

ERP vulnerabilities SHALL be:

```text
identified
triaged
risk-assessed
patched/mitigated
verified
```

through the security maintenance process.

---

# 181. Emergency patch

Critical security patches MAY use expedited release procedures but SHALL retain:

```text
review
artifact provenance
testing appropriate to risk
audit
rollback capability
```

---

# 182. Security patch versus ERP upgrade

Security fixes SHOULD be isolated from unrelated feature changes where practical.

---

# 183. Database patching

PostgreSQL security updates SHALL follow controlled maintenance procedures and compatibility testing.

---

# 184. Java runtime patching

The ERP Java runtime SHALL remain within the supported compatibility envelope and receive appropriate security updates.

---

# 185. Vulnerability exception

Unpatched known vulnerabilities requiring temporary acceptance SHALL have:

```text
owner
risk
mitigation
expiry
review date
```

---

# 186. Security event

Baobab SHOULD distinguish security events from business-domain events.

Examples:

```text
security.authentication.failed
security.authorization.denied
security.privileged-access.started
security.break-glass.used
security.credential.revoked
```

These are operational/security telemetry and need not share the ERP business-event channel.

---

# 187. Security event confidentiality

Security telemetry itself may contain sensitive information and SHALL be protected.

---

# 188. SIEM

Production security logs SHOULD be consumable by the organisation's security monitoring/SIEM capability when introduced.

---

# 189. Alerting

High-risk events SHOULD generate timely alerts.

Examples:

```text
break-glass use
System Client access
unexpected cross-tenant attempt
repeated privileged failure
credential abuse
unauthorised plugin change
```

---

# 190. Security incident traceability

Correlation IDs and principal identity SHALL allow investigators to reconstruct a security-relevant operation across:

```text
gateway
ERP API
iDempiere
event infrastructure
Control Plane
```

where logs are available.

---

# 191. Security testing

Security testing SHALL be part of ERP release qualification.

---

# 192. Authentication tests

Tests SHALL verify:

```text
missing credential
invalid credential
expired credential
wrong audience
wrong issuer
revoked credential
```

where applicable.

---

# 193. Authorization tests

Tests SHALL verify:

```text
allowed capability
denied capability
wrong Tenant
wrong LegalEntity
wrong Market
wrong DigitalEstate
wrong resource
wrong document state
```

---

# 194. Tenant isolation tests

Every shared-instance release SHALL include explicit cross-tenant tests.

Example:

```text
Tenant A creates invoice A

Tenant B:
    cannot retrieve invoice A
    cannot modify invoice A
    cannot post invoice A
    cannot discover its native mapping
```

---

# 195. Native-ID attack tests

Tests SHALL attempt to supply another Tenant's:

```text
AD_Client_ID
AD_Org_ID
record ID
```

and confirm rejection.

---

# 196. Canonical-ID attack tests

Tests SHALL attempt cross-tenant canonical UUID substitution.

---

# 197. Mapping attack tests

Tests SHALL verify that a valid canonical entity cannot resolve through another Tenant's mapping.

---

# 198. Background-worker isolation tests

Worker tests SHALL interleave multiple Tenant workloads and verify Context separation.

---

# 199. Cache isolation tests

Tests SHALL attempt cross-tenant cache-key collisions.

---

# 200. Event isolation tests

Tests SHALL verify that unauthorised consumers cannot subscribe to another Tenant's restricted financial events.

---

# 201. Replay tests

Event replay SHALL verify that duplicate financial effects cannot be generated.

---

# 202. Privilege tests

Tests SHALL verify that ordinary service identities cannot:

```text
reopen periods
modify accounting schemas
manage users
install plugins
access System Client
```

---

# 203. Break-glass tests

Break-glass mechanisms SHALL be periodically tested without compromising production data.

---

# 204. Secret scanning

Repositories SHALL use secret-detection controls.

---

# 205. Static analysis

Baobab ERP extension code SHOULD participate in appropriate static security analysis.

---

# 206. Dependency scanning

Java/OSGi dependencies SHALL be scanned for known vulnerabilities.

---

# 207. Container scanning

Production container images SHALL be scanned before deployment.

---

# 208. Dynamic testing

Security-sensitive APIs SHOULD undergo dynamic security testing appropriate to their exposure.

---

# 209. Penetration testing

Before materially sensitive production rollout, ERP external attack surfaces SHOULD receive penetration testing proportionate to risk.

---

# 210. Threat modelling

Threat modelling SHALL be revisited when introducing:

```text
new Market
new regulatory adapter
new payment integration
new public endpoint
new isolation profile
new authentication architecture
new privileged automation
```

---

# 211. Core threat classes

The ERP threat model SHALL explicitly consider:

```text
cross-tenant data access
privilege escalation
credential theft
token replay
IDOR
SQL injection
SSRF
malicious file upload
event spoofing
event replay
supply-chain compromise
insider misuse
backup disclosure
misconfiguration
```

---

# 212. Cross-tenant threat

Cross-tenant disclosure or mutation SHALL be treated as a critical architectural failure.

---

# 213. Security review gate

Any implementation that weakens:

```text
AD_Client separation
Context validation
capability authorization
native ERP roles
database isolation
```

requires explicit architecture/security review.

---

# 214. Security ownership

Security responsibilities SHALL be distributed deliberately.

```text
Identity platform:
    principal authentication

Control Plane:
    Context
    capability topology
    canonical isolation policy

Gateway:
    edge authentication
    traffic controls
    request policy

ERP API:
    capability/resource authorization

iDempiere:
    native Client/Org/Role security

Infrastructure:
    network
    compute
    database
    secrets
    encryption

Security operations:
    monitoring
    incident response
```

---

# 215. No security monoculture

No team SHALL assume:

> The gateway checked it, therefore ERP does not need to.

or:

> iDempiere has roles, therefore the Control Plane does not need tenant Context.

Defence in depth is intentional.

---

# 216. Security policy precedence

When multiple policies apply, the effective authorization SHALL use the intersection of permitted access.

Conceptually:

```text
Identity Grant
       ∩
Tenant Grant
       ∩
LegalEntity Grant
       ∩
Capability Grant
       ∩
Resource Policy
       ∩
Isolation Policy
       ∩
Native ERP Permission
       =
Effective Permission
```

---

# 217. No privilege union through ambiguity

Conflicting or ambiguous authorization SHALL fail closed.

---

# 218. Revocation

Baobab SHALL support revocation of:

```text
human sessions
service credentials
capability grants
privileged access
certificates
API credentials
```

as applicable.

---

# 219. Grant lifecycle

Authorization grants SHOULD support:

```text
pending
active
suspended
expired
revoked
```

where temporal governance is needed.

---

# 220. Temporal authorization

Temporary access SHOULD support:

```text
valid_from
valid_until
```

rather than relying on manual future removal.

---

# 221. Role change

A user's historical audit identity SHALL remain intact after their current role changes.

---

# 222. User deletion

Deleting/deactivating a user SHALL not delete historical audit records.

---

# 223. Service retirement

Retiring an integration SHALL include:

```text
revoke credentials
remove grants
disable subscriptions
remove unnecessary network access
preserve audit history
```

---

# 224. Tenant offboarding

Tenant offboarding SHALL revoke new operational access while preserving legally required financial/audit records.

---

# 225. Engine migration

During shared-to-dedicated EngineInstance migration, authorization SHALL follow the authoritative CapabilityBinding.

---

# 226. No dual-write authorization window

Migration SHALL NOT accidentally leave both old and new instances writable merely because credentials exist on both.

---

# 227. Migration credential cleanup

After cutover, obsolete credentials and network paths SHALL be revoked.

---

# 228. Disaster recovery

DR infrastructure SHALL preserve equivalent security controls.

---

# 229. DR is not security downgrade

A failover environment SHALL NOT use:

```text
shared admin password
public database
disabled authorization
unrestricted network
```

merely because it is an emergency environment.

---

# 230. Security invariants

```text
INV-ERP-SEC-001
Every tenant-sensitive ERP operation executes within trusted Context.

INV-ERP-SEC-002
Caller-supplied Tenant identifiers are never sufficient authorization.

INV-ERP-SEC-003
Authentication does not imply authorization.

INV-ERP-SEC-004
CapabilityBinding does not replace principal authorization.

INV-ERP-SEC-005
AD_Client is resolved server-side.

INV-ERP-SEC-006
AD_Org is resolved/validated server-side.

INV-ERP-SEC-007
System Client is never an ordinary business integration context.

INV-ERP-SEC-008
Cross-Client business access is denied by default.

INV-ERP-SEC-009
Canonical UUID possession does not grant access.

INV-ERP-SEC-010
Native ID possession does not grant access.

INV-ERP-SEC-011
Mappings are Context-scoped.

INV-ERP-SEC-012
Machine integrations use identifiable service/workload principals.

INV-ERP-SEC-013
Ordinary engines do not share a universal ERP superuser.

INV-ERP-SEC-014
iDempiere native security remains enabled as defence in depth.

INV-ERP-SEC-015
Application runtime does not normally use PostgreSQL superuser.

INV-ERP-SEC-016
Peer engines never receive ERP database credentials.

INV-ERP-SEC-017
ERP PostgreSQL is not publicly exposed.

INV-ERP-SEC-018
Production service traffic uses encrypted transport.

INV-ERP-SEC-019
Trusted identity headers are accepted only from trusted infrastructure.

INV-ERP-SEC-020
Tokens are issuer/audience/expiry validated.

INV-ERP-SEC-021
Production secrets are never committed to source control.

INV-ERP-SEC-022
Secrets are independently rotatable.

INV-ERP-SEC-023
Privileged access is auditable.

INV-ERP-SEC-024
Break-glass access never disables audit.

INV-ERP-SEC-025
Ownership hierarchy does not automatically grant cross-entity access.

INV-ERP-SEC-026
Tenant-sensitive cache keys include appropriate Context.

INV-ERP-SEC-027
Background workers do not use mutable global Tenant context.

INV-ERP-SEC-028
Tenant Context cannot leak across concurrent workloads.

INV-ERP-SEC-029
Event subscriptions enforce authorization.

INV-ERP-SEC-030
Event replay is privileged and consumers remain idempotent.

INV-ERP-SEC-031
DLQs receive equivalent security/residency treatment.

INV-ERP-SEC-032
Sensitive credentials never appear in normal logs.

INV-ERP-SEC-033
API errors do not expose internal stack/database details.

INV-ERP-SEC-034
Production data is not copied casually into development.

INV-ERP-SEC-035
Codespaces are not default production administration environments.

INV-ERP-SEC-036
Production build artifacts have traceable provenance.

INV-ERP-SEC-037
Unapproved plugins cannot be installed into production.

INV-ERP-SEC-038
Shared EngineInstance releases include cross-tenant security testing.

INV-ERP-SEC-039
Security policy ambiguity fails closed.

INV-ERP-SEC-040
DR does not weaken the production security model.

INV-ERP-SEC-041
Engine migration never creates uncontrolled dual-write authority.

INV-ERP-SEC-042
Revoked identities cannot retain operational access merely through stale mapping.

INV-ERP-SEC-043
Financial privilege remains capability and Context scoped.

INV-ERP-SEC-044
AI/automation receives no implicit privileged ERP authority.

INV-ERP-SEC-045
ERP security remains independent of native numeric identifier secrecy.
```

---

# 231. Canonical authorization example

Suppose the Trade Engine requests:

```http
POST /erp/v1/customer-invoices
```

for Thamani.

The decision path SHALL resemble:

```text
Trade workload identity
        │
        ▼
authenticate
        │
        ▼
Trade principal
        │
        ▼
requested Context
        │
        ▼
Tenant = Thamani
        │
        ▼
LegalEntity = authorised entity
        │
        ▼
Capability = erp.customer-invoices.create
        │
        ▼
principal capability grant?
        │
       YES
        ▼
CapabilityBinding
        │
        ▼
ERP EngineInstance
        │
        ▼
Tenant mapping
        │
        ▼
AD_Client
        │
        ▼
LegalEntity / organisation mapping
        │
        ▼
AD_Org
        │
        ▼
iDempiere service role
        │
        ▼
resource/business validation
        │
        ▼
create invoice
```

Any failed step SHALL terminate the operation.

---

# 232. Cross-tenant attack example

Assume:

```text
Trade Principal
    authorised Tenant = Thamani
```

and attacker submits:

```text
invoice_id =
canonical UUID belonging to Zuribeans
```

The system SHALL evaluate:

```text
UUID exists?
    YES

belongs to authorised Context?
    NO

therefore:
    DENY
```

It SHALL NOT evaluate:

```text
UUID exists?
    YES

therefore:
    ALLOW
```

---

# 233. Native-ID attack example

A caller sends:

```json
{
  "AD_Client_ID": 1000042
}
```

The canonical API SHALL ignore/reject this as a tenant-selection mechanism.

Native Client derives from trusted Context.

---

# 234. Shared-instance security model

```text
                    ERP EngineInstance
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      AD_Client A      AD_Client B      AD_Client C
          │                │                │
          ▼                ▼                ▼
      Tenant A         Tenant B         Tenant C

Canonical Context
       │
       ▼
server-side mapping
       │
       ▼
exactly one authorised native Client
```

---

# 235. Defence-in-depth model

```text
┌──────────────────────────────────────────────┐
│             Identity Security                │
├──────────────────────────────────────────────┤
│             Gateway Security                 │
├──────────────────────────────────────────────┤
│          Baobab Context Security             │
├──────────────────────────────────────────────┤
│        Capability Authorization              │
├──────────────────────────────────────────────┤
│         Canonical Mapping Security           │
├──────────────────────────────────────────────┤
│          ERP Application Security            │
├──────────────────────────────────────────────┤
│          iDempiere Role Security             │
├──────────────────────────────────────────────┤
│          Database / Network Security         │
├──────────────────────────────────────────────┤
│        Audit / Detection / Response           │
└──────────────────────────────────────────────┘
```

An attacker must not gain unrestricted ERP authority merely by bypassing one layer.

---

# 236. Security review checklist

Before a new ERP integration is activated, reviewers SHALL determine:

```text
Who is the principal?

Is it human or machine?

How is it authenticated?

Which Tenant may it access?

Which LegalEntity?

Which Market?

Which capabilities?

Which resources?

Which EngineInstance?

Which AD_Client?

Which AD_Org?

Which native ERP Role?

Which network path?

Which secrets/certificates?

What is logged?

How is access revoked?

What happens if the credential is stolen?

Can it cross Tenant boundaries?

Can it elevate privilege?

Can it replay operations?

Can it generate duplicate financial effects?

Does it need production data?

Does it need Internet egress?

Does it require break-glass access?

How is it tested?
```

---

# 237. Definition of done

ADR-ERP-010 SHALL be considered implemented when:

- [ ] ERP principal model is defined.
- [ ] Human and machine identities are distinct.
- [ ] Trusted Context resolution is implemented.
- [ ] Caller Tenant headers are never trusted directly.
- [ ] Capability authorization exists.
- [ ] CapabilityBinding is separate from principal grants.
- [ ] AD_Client resolution is server-side.
- [ ] AD_Org resolution is server-side.
- [ ] System Client access is restricted.
- [ ] Native service identities are least privileged.
- [ ] iDempiere roles are documented.
- [ ] Cross-client access is denied by default.
- [ ] Mapping resolution is Context-scoped.
- [ ] Database is network-isolated.
- [ ] Application runtime does not use DB superuser.
- [ ] Peer engines have no ERP DB credentials.
- [ ] Production transport encryption is enabled.
- [ ] Token issuer/audience validation exists.
- [ ] Trusted proxy policy exists.
- [ ] Secret-management architecture exists.
- [ ] Credential rotation exists.
- [ ] Certificate lifecycle exists.
- [ ] Privileged access policy exists.
- [ ] Break-glass process exists.
- [ ] MFA policy exists for privileged human access.
- [ ] Event ACLs exist.
- [ ] DLQ security exists.
- [ ] Replay authorization exists.
- [ ] Sensitive logging policy exists.
- [ ] Tenant-safe cache strategy exists.
- [ ] Worker Context isolation exists.
- [ ] Production-data handling policy exists.
- [ ] CI/CD identities are least privileged.
- [ ] Production artifacts are provenance-traceable.
- [ ] Plugin supply-chain controls exist.
- [ ] Vulnerability-management process exists.
- [ ] Cross-tenant automated tests exist.
- [ ] Native-ID substitution tests exist.
- [ ] Canonical-ID substitution tests exist.
- [ ] Mapping-isolation tests exist.
- [ ] Worker-isolation tests exist.
- [ ] Event-isolation tests exist.
- [ ] Privilege-escalation tests exist.
- [ ] Security telemetry exists.
- [ ] Revocation procedures exist.
- [ ] Tenant offboarding revokes operational access.
- [ ] Engine migration revokes obsolete authority.
- [ ] DR preserves equivalent security controls.

---

# 238. Final security model

Baobab SHALL never rely on:

```text
"the caller knows the Tenant ID"

"the UUID is difficult to guess"

"the service is internal"

"the database is on a private subnet"

"the gateway already authenticated it"

"iDempiere already has roles"

"the holding company owns the subsidiary"

"this is only a background worker"
```

as sufficient security arguments.

Instead, effective ERP authority SHALL be derived from:

```text
Authenticated Principal
          │
          ▼
Trusted Context
          │
          ▼
Explicit Capability Grant
          │
          ▼
Authoritative CapabilityBinding
          │
          ▼
Context-scoped Mapping
          │
          ▼
Native ERP Client / Organization
          │
          ▼
Least-Privilege ERP Role
          │
          ▼
Business-State Authorization
          │
          ▼
Audited Operation
```

---

# 239. Governing statement

The definitive rule is:

> **A caller may perform an ERP operation only when both its identity and the resolved business Context authorize that exact operation against that exact resource.**

And the tenant-isolation counterpart is:

> **Tenant isolation is not a filter added to ERP queries; it is an end-to-end invariant spanning identity, Context, routing, mappings, native ERP security, persistence, events, caches, observability and operations.**

This is especially important for shared iDempiere infrastructure.

A shared EngineInstance is acceptable only while Baobab can prove that sharing infrastructure does not mean sharing authority.

If that guarantee cannot be maintained for a workload, the correct response is stronger `IsolationProfile` placement—not weakening the security model.