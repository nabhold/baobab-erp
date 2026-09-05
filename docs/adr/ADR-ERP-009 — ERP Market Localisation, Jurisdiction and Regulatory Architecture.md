# ADR-ERP-009 — ERP Market Localisation, Jurisdiction and Regulatory Architecture

**Status:** Accepted  
**Decision class:** ERP / Localisation / Market / Jurisdiction / Regulatory / Internationalisation  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/infrastructure`, `nabhold/baobab-trade`, consuming Digital Estates  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-008  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL implement market and jurisdiction expansion through an explicit, governed localisation architecture rather than through:

```text
country-specific forks
one ERP deployment per country
one AD_Client per market
one AD_Org per market
hard-coded country logic
```

The ERP localisation architecture SHALL separate:

```text
Market
Jurisdiction
LegalEntity
TaxRegime
LocalisationPackage
Currency
Language
Locale
FiscalCalendar
StatutoryReportingProfile
DocumentProfile
NumberingProfile
PaymentProfile
BankingProfile
CustomsProfile
ResidencyPolicy
DeploymentRegion
```

These dimensions MAY correlate in a particular deployment.

They SHALL NOT be declared universally equivalent.

---

# 2. Governing principle

The governing rule is:

> **A market describes where Baobab conducts business; a jurisdiction describes which legal or regulatory authority applies; localisation describes how an engine must behave to operate correctly under those conditions.**

Therefore:

```text
Market != Jurisdiction
Jurisdiction != LegalEntity
Market != Currency
Market != Language
Market != EngineInstance
Jurisdiction != DeploymentRegion
Localisation != Fork
```

---

# 3. International architecture

Baobab SHALL be designed for:

```text
one legal entity
    operating in
multiple markets

multiple legal entities
    operating in
one market

one market
    involving
multiple jurisdictions

one EngineInstance
    supporting
multiple compatible localisations

one localisation
    potentially reused by
multiple legal entities
```

subject to security, accounting, regulatory and technical compatibility.

---

# 4. Market

`Market` remains a canonical Control Plane concept.

A Market represents a governed commercial operating context.

Examples might include:

```text
South Africa
Uganda
Kenya
East African regional export market
European Union commercial market
```

The exact taxonomy SHALL be defined by Baobab business governance.

---

# 5. Market does not imply incorporation

Creating:

```text
Market = Uganda
```

SHALL NOT automatically create:

```text
LegalEntity = Uganda subsidiary
```

Whether incorporation is necessary depends on actual legal, tax and business requirements.

---

# 6. Market does not imply ERP tenant

Likewise:

```text
Market
```

SHALL NOT automatically produce:

```text
AD_Client
```

or:

```text
EngineInstance
```

---

# 7. Jurisdiction

A `Jurisdiction` represents a legal or regulatory authority relevant to an operation.

Examples may include:

```text
national
provincial/state
municipal
customs territory
economic union
special economic zone
```

where business requirements justify explicit modelling.

---

# 8. Jurisdiction hierarchy

Jurisdictions MAY form hierarchies.

Conceptually:

```text
Country
   │
   ├── Province / State
   │       │
   │       └── Municipality
   │
   └── Other regulatory subdivision
```

Baobab SHALL NOT assume all countries use the same jurisdiction hierarchy.

---

# 9. Market-to-jurisdiction relationship

A Market MAY be governed by multiple jurisdictions.

A Jurisdiction MAY affect multiple Markets.

Therefore the relationship SHALL conceptually support:

```text
Market N:M Jurisdiction
```

where required.

---

# 10. Localisation

A `Localisation` is the collection of configuration, extensions, reference data, reports, processes and compliance rules necessary to operate an engine correctly in a jurisdiction or market context.

---

# 11. Localisation is not translation

Translation is one component of localisation.

Localisation MAY include:

```text
language
currency
tax
accounting
document formats
statutory reporting
payment conventions
banking conventions
fiscal rules
numbering
units
addresses
identifiers
customs
withholding
electronic invoicing
regulatory integrations
```

---

# 12. LocalisationProfile

Baobab SHOULD introduce a governed `LocalisationProfile` concept.

Conceptually:

```text
LocalisationProfile

id
code
name
status
jurisdiction_ids
supported_markets
engine
engine_version_range
package_set
configuration_version
validation_status
effective_from
effective_to
```

The physical ownership of this resource SHALL be determined by the Control Plane implementation model.

---

# 13. Localisation package

An ERP localisation package MAY contain:

```text
iDempiere OSGi plugins
Application Dictionary configuration
2Pack configuration
reference data
tax configuration
report definitions
print formats
processes
validators
integration adapters
translations
test fixtures
```

---

# 14. No core fork

A localisation SHALL NOT normally modify iDempiere upstream core.

Preferred order:

```text
configuration
     ↓
Application Dictionary
     ↓
reference data
     ↓
supported extension point
     ↓
OSGi plugin
     ↓
Baobab adapter
```

Core modification remains an exceptional ADR-governed last resort.

---

# 15. Localisation provenance

Every localisation component SHALL have identifiable provenance.

At minimum:

```text
name
version
source
maintainer
license
supported iDempiere version
build digest where applicable
```

---

# 16. Third-party localisation packages

Third-party iDempiere localisations MAY be adopted.

They SHALL first undergo:

```text
functional review
security review
license review
maintenance review
upgrade compatibility review
tenant-isolation review
schema-impact review
accounting review
```

---

# 17. Localisation trust boundary

Installing a localisation plugin is equivalent to installing executable ERP code.

It SHALL therefore be governed as production software, not treated as harmless reference data.

---

# 18. Localisation certification

A localisation SHALL have lifecycle states such as:

```text
candidate
assessing
configured
testing
certified
active
deprecated
retired
```

---

# 19. Candidate

`candidate` means:

> A potential localisation implementation has been identified.

It SHALL not be production-authorised.

---

# 20. Assessing

`assessing` means:

> Functional, legal, security, accounting and technical suitability are being evaluated.

---

# 21. Configured

`configured` means:

> Required implementation/configuration exists but has not completed production certification.

---

# 22. Testing

`testing` means:

> Automated and manual validation is underway.

---

# 23. Certified

`certified` means:

> Baobab has approved the localisation for a defined combination of engine version, jurisdiction and capability set.

---

# 24. Active

`active` means:

> Production workloads may use the localisation.

---

# 25. Certification scope

Certification SHALL be scoped.

Example:

```text
Localisation:
    South Africa ERP Financial

iDempiere:
    13.x approved baseline

Capabilities:
    procurement
    sales accounting
    AP
    AR
    inventory accounting

Legal scope:
    defined South African requirements

Certification:
    version X
```

Certification SHALL NOT mean:

> compliant forever with every possible regulation.

---

# 26. Regulatory ownership

Software architecture SHALL NOT pretend to determine legal compliance by itself.

Regulatory requirements SHALL be validated by appropriately authorised:

```text
finance
tax
legal
compliance
local domain specialists
```

where required.

---

# 27. RegulatoryRequirement

Baobab SHOULD maintain traceability between requirements and implementation.

Conceptually:

```text
RegulatoryRequirement
        │
        ▼
LocalisationControl
        │
        ▼
Implementation
        │
        ▼
ValidationEvidence
```

---

# 28. Evidence

Certification evidence MAY include:

```text
test results
configuration snapshots
sample statutory reports
accounting validation
security assessment
legal/compliance approval
integration certification
```

---

# 29. Market onboarding lifecycle

A new Market SHALL pass through a governed onboarding lifecycle.

Recommended states:

```text
requested
discovery
legal_assessment
financial_assessment
localisation_assessment
technical_design
implementation
validation
pilot
production_ready
active
suspended
retired
```

---

# 30. Market request

A Market request SHALL identify at least:

```text
business sponsor
target jurisdiction
expected legal entity
business model
products/services
expected currencies
expected transaction types
target launch period
```

---

# 31. Discovery

Discovery SHALL determine:

```text
legal structure
tax obligations
accounting requirements
currency requirements
banking requirements
payment requirements
customs requirements
statutory reporting
data residency
language
document requirements
local identifiers
```

---

# 32. No automatic country template

Country name alone SHALL NOT be considered sufficient localisation configuration.

---

# 33. Market Readiness Assessment

Baobab SHOULD maintain a formal:

```text
Market Readiness Assessment
```

for every production market.

---

# 34. Readiness dimensions

The assessment SHALL cover at least:

```text
commercial
legal
corporate
tax
accounting
currency
banking
payments
customs
privacy
data residency
security
language
documents
reporting
operational support
technical compatibility
```

---

# 35. Readiness result

Each dimension SHOULD receive a state such as:

```text
not_applicable
unknown
blocked
in_progress
validated
approved
```

---

# 36. Unknown is not approved

An unanswered regulatory question SHALL NOT silently become:

```text
approved
```

to meet a launch date.

---

# 37. Production gate

A Market SHALL not become `production_ready` until all mandatory readiness controls have been satisfied or formally risk-accepted by authorised governance.

---

# 38. Localisation matrix

Baobab SHOULD maintain a matrix:

| Capability | Market | Jurisdiction | Localisation | Status |
|---|---|---|---|---|
| ERP Finance | ZA | applicable ZA jurisdictions | ZA ERP localisation | Certified |
| ERP Finance | UG | applicable UG jurisdictions | UG ERP localisation | Candidate |
| Trade | ZA | applicable ZA jurisdictions | ZA commerce rules | Certified |
| Trade | UG | applicable UG jurisdictions | UG commerce rules | Candidate |

The actual statuses SHALL reflect real implementation state.

---

# 39. Capability-specific readiness

A Market may be ready for one capability but not another.

Example:

```text
Content:
    READY

Trade:
    READY

ERP procurement:
    READY

ERP statutory accounting:
    NOT READY
```

Baobab SHALL support this distinction.

---

# 40. No global market-ready boolean

A single:

```text
market.enabled = true
```

SHALL not be sufficient for production capability routing.

---

# 41. CapabilityBinding gate

A production `CapabilityBinding` SHALL only route to an EngineInstance/localisation combination certified for that Context.

---

# 42. Isolation compatibility

A localisation SHALL be evaluated against the `IsolationProfile`.

A plugin incompatible with safe shared-instance tenancy MAY force:

```text
dedicated EngineInstance
```

for affected workloads.

---

# 43. Localisation compatibility matrix

Each production ERP runtime SHALL maintain a compatibility matrix including:

```text
iDempiere version
Baobab ERP extension version
localisation plugin versions
database migration version
configuration version
```

---

# 44. Plugin conflicts

Two individually valid localisations MAY still be incompatible when installed together.

Therefore certification SHALL include coexistence testing for shared EngineInstances.

---

# 45. Shared instance rule

A shared ERP EngineInstance SHALL contain only localisation combinations certified to coexist.

---

# 46. Dedicated-instance trigger

A dedicated EngineInstance SHOULD be evaluated where a localisation introduces:

```text
global schema changes
incompatible dependencies
global configuration
unsafe tenant assumptions
regulatory isolation
release cadence conflicts
high operational risk
```

---

# 47. Localisation does not automatically require dedicated deployment

Conversely, geographic difference alone SHALL not force a separate ERP deployment.

---

# 48. Language

Baobab SHALL distinguish:

```text
language
locale
market
currency
```

---

# 49. Language is not Market

A South African market may require multiple languages.

A Swahili-language experience may operate across multiple markets.

---

# 50. Locale

Locale governs presentation conventions such as:

```text
date formatting
number formatting
decimal separators
display conventions
```

It SHALL not determine accounting truth.

---

# 51. Internal canonical contracts

Canonical APIs and events SHALL remain locale-neutral.

Example:

```json
{
  "amount": "1234.50",
  "currency": "ZAR",
  "accounting_date": "2026-09-02"
}
```

not locale-formatted strings such as:

```text
R 1.234,50
```

---

# 52. Presentation formatting

Locale-specific formatting belongs at presentation/reporting boundaries.

---

# 53. Translation

Translations MAY be supplied through:

```text
iDempiere language packs
localisation packages
Payload-managed customer content
Digital Estate translations
```

according to ownership.

---

# 54. ERP translation ownership

ERP translations SHALL cover ERP operational concepts.

Payload SHALL continue to own editorial/customer-facing content where applicable.

---

# 55. Currency

Market configuration MAY define:

```text
preferred commerce currencies
permitted settlement currencies
display currencies
```

but SHALL not redefine ERP functional currency.

---

# 56. Currency availability

A currency SHALL only become usable for a financial process when the required:

```text
precision
exchange-rate policy
accounting configuration
banking/payment support
```

exists.

---

# 57. Currency code

Canonical contracts SHALL use standard currency codes.

Currency SHALL always be explicit for monetary values.

---

# 58. Exchange-rate localisation

A jurisdiction MAY require particular exchange-rate sources or methodologies.

These requirements SHALL feed ADR-ERP-008's exchange-rate authority model.

---

# 59. Fiscal calendar

Jurisdictions MAY influence:

```text
tax year
reporting periods
statutory deadlines
```

but the accounting calendar remains an explicit financial configuration.

---

# 60. Fiscal calendar is not Market

Two legal entities in the same Market MAY have different fiscal calendars where legally permissible.

---

# 61. TaxRegime

Baobab SHOULD explicitly model or reference the applicable tax regime for ERP provisioning.

A TaxRegime may define:

```text
tax types
rates
effective periods
registration requirements
reporting obligations
withholding
exemptions
reverse charge rules
```

where applicable.

---

# 62. Tax temporal integrity

Every tax rule SHALL have appropriate effective dating.

---

# 63. Historical tax integrity

Changing a tax rate SHALL NOT rewrite historical posted transactions.

---

# 64. Tax registration

A legal entity MAY have different tax registrations across jurisdictions.

These registrations SHALL belong to the legal entity/jurisdiction relationship, not globally to the Market.

---

# 65. Tax identifiers

Tax identifiers SHALL be:

```text
typed
jurisdiction-scoped
validated where possible
classified as sensitive where appropriate
```

---

# 66. Tax validation

Identifier validation MAY include:

```text
format validation
checksum validation
external authority validation
```

where available and lawful.

Format validation SHALL not be confused with proof of registration.

---

# 67. Withholding

Jurisdictions requiring withholding tax SHALL implement it through approved ERP localisation/configuration.

---

# 68. Electronic invoicing

Where a jurisdiction requires:

```text
electronic invoice registration
clearance
fiscalisation
government submission
digital signature
QR codes
```

Baobab SHALL treat this as a regulated integration capability.

---

# 69. E-invoicing adapter

Government e-invoicing integrations SHALL use dedicated adapters.

Conceptually:

```text
ERP Invoice
    │
    ▼
Baobab Regulatory Adapter
    │
    ▼
Government / Fiscal Platform
```

---

# 70. No regulatory network call inside posting transaction

Where external fiscal systems are asynchronous or unreliable, ERP SHALL NOT generally hold a database transaction open across an uncontrolled government network call.

---

# 71. Regulatory workflow

Where legally permitted:

```text
ERP transaction
     ↓
transactional outbox
     ↓
regulatory adapter
     ↓
authority
     ↓
response
     ↓
ERP regulatory status
```

SHALL be preferred.

Where a jurisdiction legally requires synchronous clearance before legal issuance, a jurisdiction-specific workflow SHALL explicitly implement that requirement.

---

# 72. Regulatory status

Canonical document models MAY need statuses such as:

```text
submission_pending
submitted
accepted
rejected
cancelled
```

separate from core accounting status where necessary.

---

# 73. Government identifier

A fiscal authority's document ID SHALL normally be an ExternalReference.

It SHALL not replace the canonical document UUID.

---

# 74. Regulatory failure

Failure to submit a legally required document SHALL be:

```text
observable
retryable where lawful
reconcilable
escalated
```

and never silently discarded.

---

# 75. Statutory document profile

Baobab SHOULD define a `DocumentProfile` concept where jurisdictions impose document requirements.

It MAY govern:

```text
required fields
legal names
tax identifiers
addresses
currency display
tax breakdown
numbering
mandatory statements
QR/barcode
signature
language
```

---

# 76. Canonical versus rendered document

The canonical financial entity SHALL remain separate from its rendered statutory representation.

---

# 77. Print format

Jurisdiction-specific print/PDF layouts SHALL be version-controlled and tested where legally significant.

---

# 78. Document numbering

Document numbering SHALL be explicitly configured.

Jurisdictions may require:

```text
continuous sequences
fiscal-year resets
branch-specific sequences
document-type prefixes
government-authorised ranges
```

---

# 79. Numbering is not identity

A statutory invoice number SHALL remain a business/legal identifier.

The canonical UUID remains technical identity.

---

# 80. Numbering immutability

Once legally issued, document numbers SHALL not be casually reassigned.

---

# 81. Sequence gaps

Where jurisdictions regulate sequence gaps, Baobab SHALL implement monitoring/reconciliation appropriate to that rule.

---

# 82. Address localisation

Address formats differ across jurisdictions.

Baobab SHALL avoid a rigid universal postal-address rendering assumption.

---

# 83. Canonical address

Canonical address data SHOULD remain structurally representable while rendering follows jurisdiction/locale conventions.

---

# 84. Business identifiers

Jurisdictions may require identifiers such as:

```text
company registration
tax registration
import/export number
customs registration
branch registration
```

These SHALL be typed rather than stored in one generic ungoverned string.

---

# 85. Units of measure

Baobab SHALL maintain canonical unit semantics.

Markets may display or transact in different units.

---

# 86. Unit conversion

Conversions SHALL use explicit conversion rules.

Example:

```text
kg
tonne
lb
bag
container
```

shall not be assumed interchangeable without defined conversion semantics.

---

# 87. Commodity-specific units

For businesses such as coffee import/export, commercial units MAY include:

```text
kg
metric tonne
bag
container
```

The ERP SHALL preserve the authoritative inventory/accounting unit conversions.

---

# 88. CustomsProfile

Markets involving cross-border trade MAY require a `CustomsProfile`.

It MAY define/reference:

```text
customs jurisdiction
commodity classification
tariff treatment
country of origin
valuation rules
duty/tax handling
required documents
import/export registrations
```

---

# 89. Customs classification

Product customs classification SHALL be explicit and effective-dated where necessary.

---

# 90. Commodity codes

Codes such as tariff classifications SHALL be treated as jurisdictional classifications.

They SHALL not replace canonical Product identity.

---

# 91. Country of origin

Country of origin SHALL be distinct from:

```text
supplier country
shipping origin
warehouse location
market
legal entity jurisdiction
```

---

# 92. Customs valuation

Customs valuation MAY differ from ordinary invoice valuation.

ERP localisation SHALL support this where required.

---

# 93. Incoterms

Cross-border transactions MAY require governed Incoterms or equivalent delivery terms.

Such terms affect:

```text
risk
cost allocation
freight responsibility
customs processes
```

but SHALL not be inferred merely from destination.

---

# 94. Landed cost

Customs duties and cross-border charges SHALL integrate with ADR-ERP-008 landed-cost accounting.

---

# 95. BankingProfile

A Market/Jurisdiction MAY require a banking profile governing:

```text
account identifier formats
branch codes
clearing systems
payment rails
bank-file formats
settlement calendars
```

---

# 96. Bank account identity

Bank-account data SHALL be treated as sensitive financial information.

It SHALL not be embedded casually in canonical events.

---

# 97. PaymentProfile

Commerce/payment capability SHALL explicitly determine supported:

```text
payment methods
payment providers
currencies
settlement rules
refund capabilities
```

per Market.

---

# 98. Payment support is not ERP localisation alone

Payment-provider integration belongs to the appropriate payment/Trade boundary.

ERP receives the authoritative accounting consequence.

---

# 99. Bank file localisation

Where ERP generates payment files, jurisdiction/bank-specific formats SHALL be implemented through approved adapters or plugins.

---

# 100. Calendar localisation

Local public holidays MAY affect:

```text
banking
settlement
delivery
operations
```

but SHALL remain distinct from the accounting-period calendar.

---

# 101. Statutory reporting

Jurisdictions may require periodic:

```text
tax returns
sales reports
purchase reports
withholding reports
financial statements
regulatory extracts
```

---

# 102. Reporting authority

ERP SHALL own source financial data.

A localisation MAY provide:

```text
native ERP report
Jasper report
structured export
regulatory adapter
```

depending on requirement.

---

# 103. Regulatory report versioning

A statutory report format SHALL be versioned because regulators can change:

```text
fields
schemas
calculations
submission protocols
```

---

# 104. Effective dating

A new report format SHALL have an effective period.

Historical periods SHALL remain reproducible using the correct historical rules where required.

---

# 105. Filing is a workflow

Generating a statutory report and filing it are distinct operations.

---

# 106. Filing audit

Regulatory filing SHOULD record:

```text
period
legal entity
jurisdiction
report version
generated_at
submitted_at
submitted_by
authority reference
status
```

---

# 107. Data residency

Market onboarding SHALL evaluate data-residency requirements.

---

# 108. Residency scope

Assessment SHALL include:

```text
ERP database
replicas
backups
object storage
logs
traces
event payloads
DLQ
analytics
support exports
regulatory submissions
```

---

# 109. Market does not equal DeploymentRegion

A Market in Uganda does not automatically mean:

```text
ERP must run in Uganda
```

unless actual regulatory/business requirements demand it.

---

# 110. Deployment decision

DeploymentRegion SHALL be selected from:

```text
ResidencyPolicy
latency
availability
security
cost
operational capability
regulatory requirement
```

not country-name matching.

---

# 111. Regional gateway

Where payload residency prohibits routing through a central gateway in another region, Baobab SHALL support regional data-plane gateways.

---

# 112. Control Plane metadata

The Control Plane SHOULD store minimal regulatory metadata necessary for routing/governance.

Sensitive business data SHALL remain in its authoritative domain.

---

# 113. Privacy localisation

Market onboarding SHALL identify applicable privacy obligations.

These may affect:

```text
collection
consent
retention
cross-border transfer
data-subject rights
logging
analytics
support access
```

---

# 114. Privacy is not an ERP-only concern

Privacy requirements SHALL propagate across:

```text
ERP
Trade
Payload
Digital Estates
Intelligence
analytics
infrastructure
```

---

# 115. Retention policy

Retention MAY vary by:

```text
data class
legal entity
jurisdiction
document type
regulatory obligation
```

---

# 116. Retention versus deletion

Financial retention requirements may prohibit deletion that another privacy policy would otherwise request.

Such conflicts SHALL be resolved through legal/compliance policy, not application guesswork.

---

# 117. Security localisation

No localisation SHALL weaken Baobab baseline security.

---

# 118. Regulatory exception

Where a jurisdiction imposes a technical requirement conflicting with platform security, it SHALL trigger explicit architecture/security review.

---

# 119. Local administrative access

Some jurisdictions/contracts MAY require locally restricted administrative access.

This SHALL be expressed through:

```text
IsolationProfile
ResidencyPolicy
IAM policy
EngineInstance placement
```

rather than ad hoc administrator conventions.

---

# 120. Localisation secrets

Government, bank or tax integration credentials SHALL use the Baobab secrets-management architecture.

They SHALL never be committed to localisation packages.

---

# 121. Certificate management

Regulatory integrations requiring certificates SHALL support:

```text
issuance
secure storage
rotation
expiry monitoring
revocation
audit
```

---

# 122. Market-specific endpoints

External government/banking endpoint URLs SHALL be configuration.

They SHALL not be hard-coded into domain logic.

---

# 123. Sandbox versus production

Where regulators/providers offer certification environments, Baobab SHALL maintain explicit:

```text
sandbox
certification
production
```

configuration separation.

---

# 124. No production credential reuse

Production regulatory credentials SHALL not be reused in development/test environments.

---

# 125. Market configuration hierarchy

Configuration SHOULD follow a controlled precedence model.

Conceptually:

```text
Baobab global defaults
        ↓
Engine defaults
        ↓
LocalisationProfile
        ↓
Jurisdiction
        ↓
LegalEntity
        ↓
Market
        ↓
explicit approved override
```

The exact precedence SHALL be defined per configuration type.

---

# 126. No blind inheritance

Security, tax and financial settings SHALL NOT inherit through this hierarchy unless explicitly defined as inheritable.

---

# 127. Most-specific does not always win

For security/regulatory constraints:

> strongest applicable rule wins

may supersede ordinary configuration specificity.

---

# 128. Regulatory conflict

If two applicable jurisdictions impose conflicting requirements, Baobab SHALL fail readiness assessment until the conflict has an approved resolution.

---

# 129. Localisation configuration authority

The Control Plane SHALL own:

```text
which localisation is approved
where it applies
which EngineInstance may serve it
which capability may use it
```

ERP SHALL own the detailed native configuration implementing that localisation.

---

# 130. ERP cannot self-authorise a Market

Installing a plugin in iDempiere SHALL NOT automatically make a Market production-ready.

---

# 131. CapabilityBinding enforcement

Before activating a Market's ERP binding:

```text
Market
    ↓
Jurisdiction requirements
    ↓
LocalisationProfile
    ↓
Certification
    ↓
Isolation compatibility
    ↓
EngineInstance compatibility
    ↓
CapabilityBinding ACTIVE
```

---

# 132. Runtime Context

Resolved ERP Context SHOULD carry/reference sufficient information to enforce applicable:

```text
tenant
legal entity
market
jurisdiction where needed
localisation
capability
EngineInstance
```

without trusting arbitrary caller headers.

---

# 133. No caller-selected localisation

A Digital Estate SHALL NOT be able to request:

```text
use-localisation=ZA
```

to bypass resolved Context.

---

# 134. Regulatory adapter boundary

External regulatory systems SHALL not be allowed to dictate internal ERP schema.

Adapters SHALL translate:

```text
Baobab / ERP semantics
       ↕
external regulatory protocol
```

---

# 135. Protocol replacement

If a regulator changes:

```text
SOAP → REST
XML → JSON
file upload → API
```

the canonical ERP domain model SHOULD remain stable.

---

# 136. Regulatory events

Where useful, canonical events MAY include:

```text
regulatory.document.submitted.v1
regulatory.document.accepted.v1
regulatory.document.rejected.v1
regulatory.filing.completed.v1
```

These SHOULD remain separate from core accounting events where semantics differ.

---

# 137. Event residency

Regulatory event payloads SHALL obey the applicable ResidencyPolicy.

---

# 138. Event minimisation

Do not publish entire tax returns or invoices merely because an event occurred.

Events SHOULD contain identifiers and required facts, with authorised consumers retrieving details through appropriate APIs where necessary.

---

# 139. Change monitoring

Production Markets SHALL have a process for identifying relevant regulatory changes.

---

# 140. Regulatory change lifecycle

Recommended:

```text
change_detected
     ↓
impact_assessed
     ↓
requirement_approved
     ↓
implementation
     ↓
validation
     ↓
deployment
     ↓
effective_date
     ↓
post-implementation verification
```

---

# 141. Regulatory effective date

A regulatory implementation SHALL distinguish:

```text
software deployment date
```

from:

```text
legal effective date
```

They are often different.

---

# 142. Future-effective rules

Rules MAY be deployed before their legal effective date.

Activation SHALL be effective-date controlled.

---

# 143. Emergency regulatory change

Urgent legal changes MAY use expedited release procedures.

They SHALL not bypass:

```text
audit
testing appropriate to risk
approval
rollback planning
```

---

# 144. Versioned localisation

Localisation versions SHALL be independently identifiable.

Example:

```text
za-finance-localisation 2.3.0
```

rather than relying solely on:

```text
iDempiere 13
```

---

# 145. Engine upgrade

An iDempiere upgrade SHALL trigger revalidation of all installed production localisations.

---

# 146. Localisation upgrade

A localisation upgrade SHALL trigger relevant:

```text
financial
tax
document
integration
tenant-isolation
```

regression tests.

---

# 147. Shared EngineInstance upgrade

For a shared instance, upgrade SHALL consider every active localisation hosted there.

---

# 148. Upgrade blocker

If localisation A supports a new iDempiere version but localisation B does not, the shared EngineInstance SHALL NOT be upgraded blindly.

Options include:

```text
delay upgrade
upgrade localisation B
move affected tenant
create dedicated EngineInstance
```

---

# 149. Schema migration

Localisation schema changes SHALL follow controlled migration practices.

No plugin SHALL casually execute destructive production schema mutation at startup.

---

# 150. Reference-data migration

Changes to tax codes, document types or regulatory classifications SHALL preserve historical interpretation.

---

# 151. Configuration drift

Baobab SHOULD detect drift between:

```text
certified localisation configuration
```

and:

```text
observed production configuration
```

---

# 152. Drift response

Material regulatory drift SHALL trigger:

```text
alert
assessment
possible quarantine
```

depending on severity.

---

# 153. Localisation observability

Recommended metrics include:

```text
regulatory_submission_total
regulatory_submission_failure_total
regulatory_rejection_total
localisation_validation_failure_total
certificate_expiry_seconds
statutory_report_failure_total
market_readiness_control_failure_total
```

---

# 154. Sensitive metrics

Tax numbers, invoice numbers and regulatory payload contents SHALL not be metric labels.

---

# 155. Operational dashboard

For each active Market, operations SHOULD eventually be able to see:

```text
Market status
ERP capability status
Localisation version
EngineInstance
certification status
regulatory integration health
certificate health
unresolved compliance failures
```

---

# 156. Audit query

Baobab SHALL eventually be able to answer:

> Which localisation configuration processed this financial document?

> Which version was active?

> Which jurisdictional rules applied?

> Which EngineInstance processed it?

> Which legal entity owned it?

> Which Market Context initiated it?

---

# 157. Market retirement

A Market MAY be retired without deleting its historical ERP records.

---

# 158. Retirement sequence

Recommended:

```text
stop new commercial intake
       ↓
settle open transactions
       ↓
complete regulatory filings
       ↓
disable new CapabilityBindings
       ↓
retain financial/statutory history
       ↓
retire Market
```

---

# 159. Market suspension

Temporary suspension SHALL prevent prohibited new activity while preserving:

```text
audit
reporting
settlement
regulatory obligations
```

as authorised.

---

# 160. Localisation retirement

A retired localisation version SHALL remain identifiable for historical audit.

---

# 161. Country exit

Exiting a country SHALL not imply deleting:

```text
legal entities
invoices
payments
tax filings
mappings
events
```

subject to applicable retention policy.

---

# 162. New Market checklist

Before production launch, Baobab SHALL answer:

```text
What LegalEntity trades?

Which Tenant governs it?

Which Market is being activated?

Which jurisdictions apply?

Which ERP capabilities are needed?

Which EngineInstance serves them?

Which IsolationProfile applies?

Which LocalisationProfile applies?

Which accounting schema applies?

Which functional currencies apply?

Which transaction currencies are permitted?

Which tax regime applies?

Which statutory documents are required?

Which regulatory reports are required?

Which banking/payment rails are required?

Which customs requirements apply?

Which languages/locales are required?

Which data-residency restrictions apply?

Which retention requirements apply?

Which integrations require certificates/secrets?

Has the localisation been certified?

Has financial regression passed?

Has tenant-isolation testing passed?

Has production readiness been approved?
```

---

# 163. Africa-first, not Africa-hard-coded

Baobab SHALL support African operating contexts as a primary design objective.

It SHALL NOT encode:

```text
Africa = one regulatory model
```

Africa consists of multiple independent legal, fiscal, banking, customs, currency and data-governance environments.

---

# 164. Country assumptions

No implementation SHALL assume all African Markets use:

```text
same tax structure
same currency model
same banking rails
same customs rules
same fiscal calendar
same data-residency rules
same company identifiers
same invoice requirements
```

---

# 165. Global extensibility

The same architecture SHALL permit future expansion outside Africa without redesigning the canonical platform.

---

# 166. Rejected alternative — one code fork per country

**Rejected.**

It destroys upgradeability and creates divergent ERP products.

---

# 167. Rejected alternative — one EngineInstance per Market

**Rejected as universal rule.**

Deployment follows isolation/residency/compatibility requirements.

---

# 168. Rejected alternative — Market equals AD_Client

**Rejected.**

Market is commercial context, not ERP tenancy.

---

# 169. Rejected alternative — Market equals AD_Org

**Rejected.**

Market is not automatically an accounting organisation.

---

# 170. Rejected alternative — Market equals currency

**Rejected.**

Markets can be multi-currency.

---

# 171. Rejected alternative — Market equals language

**Rejected.**

Markets can be multilingual and languages cross Markets.

---

# 172. Rejected alternative — Jurisdiction equals DeploymentRegion

**Rejected.**

Law and infrastructure placement are different dimensions.

---

# 173. Rejected alternative — installing localisation plugin means compliance

**Rejected.**

Production readiness requires certification and governance.

---

# 174. Rejected alternative — country-specific logic in Digital Estates

**Rejected for ERP regulatory authority.**

Digital Estates may localise customer experience but SHALL not reproduce statutory ERP logic.

---

# 175. Rejected alternative — hard-code tax rates

**Rejected.**

Tax rules are governed, temporal configuration.

---

# 176. Rejected alternative — hard-code government endpoints

**Rejected.**

Regulatory integrations require configurable adapters.

---

# 177. Rejected alternative — government ID becomes canonical document ID

**Rejected.**

It is an external/regulatory reference.

---

# 178. Rejected alternative — regulatory network calls from arbitrary validators

**Rejected.**

External integrations require controlled transactional boundaries.

---

# 179. Rejected alternative — global regulatory event payload replication

**Rejected.**

Residency and data minimisation apply.

---

# 180. Non-negotiable invariants

```text
INV-ERP-LOC-001
Market is not equivalent to Jurisdiction.

INV-ERP-LOC-002
Market is not equivalent to LegalEntity.

INV-ERP-LOC-003
Market is not equivalent to AD_Client.

INV-ERP-LOC-004
Market is not equivalent to AD_Org.

INV-ERP-LOC-005
Market is not equivalent to EngineInstance.

INV-ERP-LOC-006
Market is not equivalent to currency.

INV-ERP-LOC-007
Market is not equivalent to language.

INV-ERP-LOC-008
Jurisdiction is not equivalent to DeploymentRegion.

INV-ERP-LOC-009
Localisation does not require an iDempiere core fork.

INV-ERP-LOC-010
Third-party localisation code is security-reviewed.

INV-ERP-LOC-011
Localisation compatibility is versioned.

INV-ERP-LOC-012
Localisation certification has explicit scope.

INV-ERP-LOC-013
Installing a localisation does not self-authorise production use.

INV-ERP-LOC-014
CapabilityBinding activation requires compatible certified localisation.

INV-ERP-LOC-015
Shared EngineInstances host only compatible localisation sets.

INV-ERP-LOC-016
Regulatory requirements are effective-dated where applicable.

INV-ERP-LOC-017
Historical financial records retain historical regulatory interpretation.

INV-ERP-LOC-018
Tax rates are not hard-coded in application logic.

INV-ERP-LOC-019
Canonical APIs remain locale-neutral.

INV-ERP-LOC-020
Currency remains explicit in canonical money.

INV-ERP-LOC-021
Language does not determine currency.

INV-ERP-LOC-022
Locale does not determine accounting truth.

INV-ERP-LOC-023
Government document identifiers remain external references.

INV-ERP-LOC-024
Statutory numbering does not replace canonical identity.

INV-ERP-LOC-025
Regulatory credentials never reside in source-controlled localisation packages.

INV-ERP-LOC-026
Regulatory integrations are isolated behind adapters.

INV-ERP-LOC-027
Regulatory integration failure is observable and reconcilable.

INV-ERP-LOC-028
Customs classification does not replace Product identity.

INV-ERP-LOC-029
Country of origin is distinct from Market.

INV-ERP-LOC-030
Customs valuation may differ from commercial invoice valuation.

INV-ERP-LOC-031
Data residency applies to backups, logs and events as well as primary databases.

INV-ERP-LOC-032
Production regulatory credentials are environment-isolated.

INV-ERP-LOC-033
Unknown compliance status never silently becomes approved.

INV-ERP-LOC-034
Regulatory conflicts fail readiness until resolved or formally governed.

INV-ERP-LOC-035
Software deployment date and regulatory effective date are distinct.

INV-ERP-LOC-036
Engine upgrades trigger localisation compatibility validation.

INV-ERP-LOC-037
Localisation upgrades trigger financial/regulatory regression.

INV-ERP-LOC-038
Material localisation drift is observable.

INV-ERP-LOC-039
Market retirement preserves legally required history.

INV-ERP-LOC-040
Localisation SHALL preserve engine replaceability and canonical contracts.
```

---

# 181. Production Market onboarding workflow

```text
                    MARKET REQUEST
                          │
                          ▼
                 Business Discovery
                          │
                          ▼
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Legal Review      Finance/Tax       Technical
                         Review           Review
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                 Jurisdiction Model
                          │
                          ▼
                LocalisationProfile
                          │
                          ▼
             Localisation Implementation
                          │
                          ▼
                 Automated Testing
                          │
                          ▼
             Financial Regression Testing
                          │
                          ▼
             Regulatory Validation
                          │
                          ▼
                Security Validation
                          │
                          ▼
               Isolation Validation
                          │
                          ▼
                   Pilot / UAT
                          │
                          ▼
                Production Approval
                          │
                          ▼
                CapabilityBinding
                          │
                          ▼
                    ACTIVE MARKET
```

---

# 182. Runtime architecture

```text
Digital Estate / Trade / Internal Consumer
                    │
                    ▼
               API Gateway
                    │
                    ▼
             Trusted Context
                    │
                    ▼
            Control Plane Resolver
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
     Market     LegalEntity   Capability
        │           │            │
        └───────────┼────────────┘
                    ▼
             LocalisationPolicy
                    │
                    ▼
             IsolationProfile
                    │
                    ▼
            CapabilityBinding
                    │
                    ▼
              EngineInstance
                    │
                    ▼
                 iDempiere
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Tax      Accounting  Documents
          │         │         │
          └─────────┼─────────┘
                    ▼
           Regulatory Adapters
                    │
                    ▼
       Tax / Customs / Banking /
         Government Authorities
```

---

# 183. Market readiness record

The Control Plane SHOULD eventually support a machine-readable readiness representation conceptually similar to:

```json
{
  "market_id": "<uuid>",
  "capability": "erp.finance",
  "status": "production_ready",
  "legal_entity_id": "<uuid>",
  "localisation_profile_id": "<uuid>",
  "engine_instance_id": "<uuid>",
  "controls": {
    "legal": "approved",
    "tax": "approved",
    "accounting": "approved",
    "currency": "approved",
    "banking": "approved",
    "customs": "approved",
    "privacy": "approved",
    "residency": "approved",
    "security": "approved",
    "localisation": "certified"
  }
}
```

This example defines architecture semantics, not the final REST schema.

---

# 184. Initial regional strategy

Baobab SHALL begin with the Markets actually required by the operating businesses.

It SHALL NOT attempt to implement every African localisation before product-market need exists.

Instead:

```text
canonical architecture
       +
repeatable Market onboarding
       +
versioned localisation framework
       +
certification process
```

provides the expansion mechanism.

---

# 185. Market expansion rule

Adding a new Market SHOULD ordinarily require:

```text
configuration
localisation
regulatory adapters
validation
CapabilityBinding
```

rather than:

```text
new platform architecture
```

If adding a country repeatedly requires changing core platform abstractions, the canonical architecture is insufficient and SHALL be reviewed.

---

# 186. Definition of done

ADR-ERP-009 SHALL be considered implemented when:

- [ ] Market and Jurisdiction are distinct concepts.
- [ ] Jurisdiction relationships are representable.
- [ ] LocalisationProfile contract exists.
- [ ] Localisation lifecycle exists.
- [ ] Market readiness lifecycle exists.
- [ ] Capability-specific readiness is supported.
- [ ] Production CapabilityBinding requires readiness.
- [ ] Localisation compatibility matrix exists.
- [ ] Third-party localisation review process exists.
- [ ] iDempiere version compatibility is recorded.
- [ ] Shared-instance localisation coexistence is tested.
- [ ] Language is independent of Market.
- [ ] Locale-neutral canonical contracts exist.
- [ ] Currency configuration follows ADR-ERP-008.
- [ ] TaxRegime/equivalent configuration is governed.
- [ ] Tax rules are effective-dated.
- [ ] Tax identifiers are jurisdiction-scoped.
- [ ] Statutory DocumentProfile mechanism exists where required.
- [ ] Document numbering is jurisdiction-aware where required.
- [ ] Regulatory adapters are isolated from core ERP.
- [ ] Government IDs are external references.
- [ ] Regulatory submission is observable/reconcilable.
- [ ] CustomsProfile exists where cross-border trade requires it.
- [ ] Commodity classifications are governed.
- [ ] Country-of-origin semantics are explicit.
- [ ] Landed-cost integration follows ADR-ERP-008.
- [ ] Banking/payment localisation boundaries are defined.
- [ ] Data-residency assessment is mandatory.
- [ ] Privacy assessment is mandatory.
- [ ] Regulatory secrets use secrets management.
- [ ] Certificates have lifecycle monitoring.
- [ ] Sandbox/certification/production credentials are separated.
- [ ] Regulatory effective dates are supported.
- [ ] Localisation upgrades trigger regression tests.
- [ ] iDempiere upgrades trigger localisation revalidation.
- [ ] Localisation configuration drift is detectable.
- [ ] Market retirement preserves statutory history.
- [ ] Market readiness evidence is auditable.

---

# 187. Governing architectural model

For every ERP transaction Baobab SHALL be able to answer independently:

```text
WHO?
    Tenant / LegalEntity

WHERE IS BUSINESS CONDUCTED?
    Market

WHICH LAW OR REGULATION APPLIES?
    Jurisdiction

HOW MUST ERP BE CONFIGURED?
    LocalisationProfile

WHAT FINANCIAL RULES APPLY?
    Accounting / Tax Configuration

WHERE MAY THE DATA LIVE?
    ResidencyPolicy

HOW STRONGLY MUST IT BE ISOLATED?
    IsolationProfile

WHERE DOES THE SOFTWARE ACTUALLY RUN?
    EngineInstance / DeploymentRegion

WHICH ERP REPRESENTATION IS USED?
    Mapping / ExternalReference
```

No single field SHALL be expected to answer all of these questions.

---

# 188. Final governing statement

Baobab SHALL not internationalise by accumulating:

```text
if country == "ZA"
if country == "UG"
if country == "KE"
...
```

throughout its engines.

It SHALL internationalise through:

```text
canonical Context
        +
Market
        +
Jurisdiction
        +
versioned LocalisationProfile
        +
financial configuration
        +
regulatory adapters
        +
ResidencyPolicy
        +
IsolationProfile
        +
CapabilityBinding
```

The decisive principle is:

> **Countries and markets introduce policy and configuration; they must not fracture the platform architecture.**

A new Market may require substantial legal, accounting, tax, customs, banking and regulatory engineering.

It should not require Baobab to become a different platform.

That distinction is what allows the ERP Engine to grow from the initial Nabhold operating environment into a genuinely multi-market enterprise platform without accumulating country forks that eventually become impossible to secure, reconcile or upgrade.