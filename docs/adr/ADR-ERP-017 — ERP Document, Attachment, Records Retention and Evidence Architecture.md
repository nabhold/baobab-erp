# ADR-ERP-017 — ERP Document, Attachment, Records Retention and Evidence Architecture

**Status:** Accepted  
**Decision class:** ERP / Documents / Records / Evidence / Retention / Object Storage / Compliance  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, Payload CMS engine, Digital Estates, Trade Engine, object-storage infrastructure, regulatory adapters and external document services  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-016  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL distinguish **business records, rendered documents, attachments, content assets and evidentiary artifacts** as separate concepts.

iDempiere SHALL remain authoritative for ERP business records and their financial/legal state.

Binary artifacts SHALL be stored through approved document/object-storage capabilities rather than being indiscriminately embedded in ERP database rows, APIs or events.

Payload CMS SHALL remain authoritative for managed editorial/content assets and SHALL NOT become the authoritative financial-record repository.

The governing principle is:

> **The ERP record establishes the business fact; a document may render, support or evidence that fact, but the binary file is not itself the accounting authority.**

Therefore:

```text
Business Record
      !=
Rendered Document
      !=
Attachment
      !=
Content Asset
      !=
Evidence
```

---

# 2. Problem

ERP processes produce or consume substantial documentary evidence:

```text
Purchase Orders
Sales Orders
Supplier Invoices
Customer Invoices
Credit Notes
Receipts
Statements
Contracts
Bills of Lading
Packing Lists
Certificates of Origin
Inspection Certificates
Customs Declarations
Tax Documents
Payment Evidence
Bank Statements
Delivery Notes
Goods Receipt Evidence
Regulatory Acknowledgements
```

These artifacts have different:

```text
authorities
retention periods
security classifications
immutability requirements
residency requirements
access policies
```

A single generic `attachment` abstraction is insufficient.

---

# 3. Five principal concepts

Baobab SHALL distinguish:

```text
ERP Business Record
Rendered Business Document
Supporting Attachment
Managed Content Asset
Evidence Artifact
```

---

# 4. ERP Business Record

An ERP Business Record is authoritative structured business state.

Examples:

```text
CustomerInvoice
SupplierInvoice
PurchaseOrder
Payment
GoodsReceipt
Shipment
Journal
```

Its authority resides in iDempiere where the ERP domain owns that state.

---

# 5. Rendered Business Document

A rendered document is a human-readable representation of structured business state.

Examples:

```text
PDF tax invoice
PDF purchase order
customer statement
credit note PDF
goods receipt report
```

---

# 6. Rendered document is not the ledger

A PDF invoice SHALL NOT become the accounting authority merely because it is immutable.

The authoritative financial state remains ERP.

---

# 7. Supporting Attachment

A supporting attachment is an external artifact associated with a business record.

Examples:

```text
supplier PDF invoice
signed delivery note
photograph
inspection report
certificate
spreadsheet
shipping document
```

---

# 8. Managed Content Asset

A managed content asset is primarily editorial/presentation content.

Examples:

```text
Product image
campaign image
brochure
marketing PDF
website download
brand asset
```

Payload CMS MAY own such assets.

---

# 9. Evidence Artifact

An Evidence Artifact is retained specifically because it helps establish:

```text
what occurred
what was approved
what was received
what was submitted
what was accepted
what version existed
```

at a particular time.

---

# 10. Evidence may overlap with documents

A rendered invoice may also be evidence.

A supplier invoice attachment may also be evidence.

The concepts remain distinct because evidence introduces additional preservation requirements.

---

# 11. Canonical Document identity

Where documents must participate across engines, Baobab SHOULD assign canonical document/evidence identity independent of storage location.

---

# 12. Blob identity

The binary object itself SHOULD have immutable content identity based on cryptographic digest.

Conceptually:

```text
DocumentRecord UUID
        │
        ▼
DocumentVersion UUID
        │
        ▼
ObjectReference
        │
        ▼
SHA-256 digest
```

---

# 13. Business identity versus content identity

These SHALL remain separate:

```text
Canonical document UUID
    = business/platform identity

Object key
    = storage identity

Cryptographic digest
    = content integrity identity
```

---

# 14. Object storage

Binary artifacts SHOULD normally be stored in approved object storage.

ERP relational storage SHALL primarily contain metadata and references.

---

# 15. No arbitrary database BLOB strategy

Baobab SHALL NOT establish:

> Store every enterprise file directly inside PostgreSQL.

as the default document architecture.

---

# 16. Database responsibility

PostgreSQL SHALL retain transactional metadata such as:

```text
document identity
business relationship
object reference
media type
size
digest
classification
retention policy
version
created_at
created_by
```

where appropriate.

---

# 17. Storage abstraction

Applications SHALL consume a Baobab storage/document abstraction rather than depending directly on cloud-provider bucket identifiers.

---

# 18. Cloud independence

Canonical document metadata SHALL NOT contain AWS-specific infrastructure identifiers as business identity.

AWS may remain the initial deployment platform without becoming the canonical contract.

---

# 19. Object reference

An object reference SHALL identify a controlled storage object.

It SHALL NOT automatically be a publicly accessible URL.

---

# 20. Private-by-default

ERP documents and attachments SHALL be private by default.

---

# 21. Signed access

Temporary signed access MAY be generated after authorization.

---

# 22. Authorization before URL issuance

A signed object URL SHALL only be issued after:

```text
principal authentication
Context resolution
resource authorization
classification check
retention/legal policy check
```

where applicable.

---

# 23. URL lifetime

Signed URLs SHALL be short-lived and purpose-limited.

---

# 24. No permanent public ERP URLs

ERP financial documents SHALL NOT use permanent anonymous public URLs.

---

# 25. Document metadata

A document record SHOULD include conceptually:

```text
id
canonical_entity_id
document_type
record_type
title
media_type
classification
status
retention_policy
legal_hold
created_at
created_by
```

---

# 26. Document version

Version metadata SHOULD include:

```text
version_id
document_id
object_reference
sha256
size_bytes
media_type
created_at
created_by
source
```

---

# 27. Business relationship

Documents SHALL connect to business records through explicit relationships.

Example:

```text
SupplierInvoice
      │
      ├── supplier-original-invoice
      ├── customs-document
      └── approval-evidence
```

---

# 28. Relationship is typed

Generic:

```text
attached_to
```

SHOULD be supplemented with typed semantics where they matter.

---

# 29. Document types

Examples include:

```text
purchase_order
supplier_invoice
customer_invoice
credit_note
delivery_note
bill_of_lading
certificate_of_origin
customs_declaration
inspection_certificate
payment_evidence
contract
statement
```

---

# 30. Document type governance

Document types shared across engines SHALL be governed through `nabhold/shared`.

---

# 31. MIME type is not document type

```text
application/pdf
```

describes representation format.

It does not establish that the document is a:

```text
tax invoice
```

---

# 32. Filename is not authority

Filename SHALL never determine legal/document semantics.

---

# 33. Original filename

Original filename MAY be retained as metadata.

It SHALL be treated as untrusted input.

---

# 34. Upload architecture

Document upload SHALL conceptually follow:

```text
Client
  │
  ▼
Authenticated API
  │
  ▼
Authorization
  │
  ▼
Upload Session
  │
  ▼
Quarantine Storage
  │
  ▼
Validation / Scan
  │
  ▼
Digest
  │
  ▼
Approved Storage
  │
  ▼
Document Metadata
  │
  ▼
Business Record Link
```

---

# 35. Quarantine

Untrusted uploads SHOULD remain quarantined until required validation completes.

---

# 36. Malware scanning

Untrusted files SHALL be subject to malware/security scanning according to risk.

---

# 37. File validation

Validation SHOULD include:

```text
declared media type
detected media type
size
extension
malware
format integrity
policy
```

---

# 38. Extension is insufficient

A `.pdf` filename SHALL NOT prove the object is a valid PDF.

---

# 39. Executable content

Executable or active content SHALL be prohibited unless an explicit business requirement and security review permit it.

---

# 40. Archive bombs

Compressed/archive uploads SHALL have bounded extraction/security controls where supported.

---

# 41. Size limits

Upload size limits SHALL be configurable by document class/capability.

---

# 42. Content integrity

Accepted evidence artifacts SHOULD receive a cryptographic digest.

SHA-256 or a successor approved by platform security SHALL be used.

---

# 43. Digest verification

Digest SHALL be verifiable during:

```text
retrieval
migration
backup restoration
evidence validation
```

---

# 44. Digest is not authenticity

A digest proves content consistency.

It does NOT independently prove:

```text
who created the file
who signed it
whether its claims are true
```

---

# 45. Digital signature

Where stronger authenticity is required, Baobab MAY support:

```text
digital signatures
qualified signatures
regulatory signatures
provider signatures
```

according to jurisdiction.

---

# 46. Signature evidence

Signature metadata SHALL be preserved separately from raw document content where appropriate.

---

# 47. Timestamp evidence

Trusted timestamp evidence MAY be retained where legal/regulatory requirements justify it.

---

# 48. Immutability

Evidence that must demonstrate historical state SHALL be immutable after finalisation.

---

# 49. Append, do not overwrite

A corrected evidentiary document SHALL normally create:

```text
Version 2
```

rather than overwrite:

```text
Version 1
```

---

# 50. Historical version

Previous versions SHALL remain retrievable for authorised audit where retention policy requires.

---

# 51. Version lifecycle

A document MAY move through:

```text
draft
uploaded
quarantined
validated
active
superseded
archived
destroyed
```

depending on type.

---

# 52. Evidence lifecycle

Evidence MAY require stronger states:

```text
captured
sealed
retained
legal_hold
released
destroyed
```

---

# 53. Business document finalisation

Finalisation SHALL be tied to authoritative business lifecycle.

Example:

```text
ERP Customer Invoice posted
        │
        ▼
Final invoice rendering
        │
        ▼
Digest
        │
        ▼
Evidence retention
```

---

# 54. Draft invoice

A draft invoice rendering SHALL NOT be represented as final statutory evidence.

---

# 55. Final invoice

The final document SHOULD identify the authoritative ERP document/version from which it was rendered.

---

# 56. Deterministic rendering

Where practical, document generation SHOULD be reproducible from:

```text
authoritative business state
template version
locale
rendering version
```

---

# 57. Template version

Final evidence SHOULD preserve which template/version produced it.

---

# 58. Template ownership

Document templates MAY be maintained through:

```text
ERP configuration
document-generation service
Payload
source-controlled templates
```

depending on use case.

---

# 59. Template does not own financial facts

A template system SHALL not become authority over invoice amounts, tax or accounting state.

---

# 60. Payload boundary

Payload CMS MAY manage:

```text
brand assets
layout fragments
logos
customer-facing static content
marketing documents
```

---

# 61. Payload SHALL NOT own

Payload SHALL NOT become authoritative for:

```text
posted invoice state
invoice numbering
tax accounting
payment evidence
financial audit
retention decisions for ERP records
```

---

# 62. Rendering composition

A rendering service MAY combine:

```text
ERP financial facts
+
approved brand/template assets
```

to generate a final document.

---

# 63. Composition boundary

Payload-provided assets SHALL be presentation inputs, not financial inputs.

---

# 64. Customer Invoice rendering

Conceptually:

```text
iDempiere
   │
   │ authoritative invoice
   ▼
Document Service
   │
   ├── template
   ├── brand assets
   ├── locale
   └── regulatory format
   │
   ▼
Final Invoice Artifact
   │
   ▼
Object Storage
```

---

# 65. Supplier invoice

For supplier invoices:

```text
Supplier Original PDF
        │
        ▼
Document/Evidence Store
        │
        ▼
ERP Supplier Invoice
```

The uploaded supplier file and ERP structured invoice remain distinct.

---

# 66. OCR/extraction

Document extraction/OCR MAY assist creation of structured ERP data.

---

# 67. Extraction is not authority

Extracted values SHALL be considered:

```text
proposed
derived
```

until validated according to workflow.

---

# 68. AI extraction

The Intelligence Engine MAY extract:

```text
invoice number
supplier
date
amount
currency
line items
```

from uploaded documents.

---

# 69. AI confidence

AI-extracted fields SHOULD carry confidence/provenance where useful.

---

# 70. No autonomous financial truth

AI extraction SHALL NOT make an invoice financially authoritative by itself.

---

# 71. Validation

High-risk extracted financial data SHALL pass through deterministic validation and/or approval.

---

# 72. Original evidence preservation

The original supplier artifact SHALL be preserved even after successful extraction where retention policy requires it.

---

# 73. Document transformation

Conversions such as:

```text
DOCX → PDF
image → PDF
PDF → archival representation
```

SHALL preserve provenance.

---

# 74. Original versus derivative

The system SHALL distinguish:

```text
original
derived
rendered
thumbnail
preview
```

---

# 75. Preview

Preview artifacts SHALL NOT be treated as authoritative evidence.

---

# 76. Thumbnail

Thumbnail SHALL never replace the original object.

---

# 77. Retention policy

Retention SHALL be policy-driven.

Baobab SHALL NOT hard-code one universal retention period.

---

# 78. Retention dimensions

Retention MAY depend on:

```text
document type
record type
LegalEntity
Jurisdiction
Market
business purpose
financial period
contract
litigation
privacy requirements
```

---

# 79. Retention start event

Retention periods SHALL specify their start trigger.

Examples:

```text
document creation
financial period close
contract termination
employee departure
case closure
```

---

# 80. Retention policy record

A retention policy SHOULD conceptually include:

```text
policy_id
classification
scope
retention_rule
start_trigger
minimum_retention
maximum_retention where permitted
destruction_rule
authority
effective dates
```

---

# 81. No invented retention

Engineering SHALL NOT invent legal retention periods.

Finance/legal/compliance SHALL approve applicable requirements.

---

# 82. Legal hold

Legal hold SHALL override normal destruction where applicable.

---

# 83. Legal hold scope

Hold MAY apply to:

```text
specific document
business entity
Party
case
LegalEntity
date range
document class
```

---

# 84. Hold is explicit

Legal hold SHALL be represented as governed metadata/state.

---

# 85. Hold audit

Creation, modification and release of legal hold SHALL be auditable.

---

# 86. Destruction prohibited under hold

No retention process SHALL destroy an object under active legal hold.

---

# 87. Retention expiration

Expiration does not automatically mean immediate deletion.

It means the object becomes eligible for disposition according to policy.

---

# 88. Disposition

Disposition MAY be:

```text
destroy
archive
review
transfer
anonymise
retain
```

---

# 89. Destruction authorization

Sensitive or regulated records MAY require approved destruction workflow.

---

# 90. Destruction evidence

Where required, Baobab SHOULD retain metadata proving:

```text
what was destroyed
when
under which policy
by which process/authority
```

without retaining the destroyed content.

---

# 91. Cryptographic erasure

Where appropriate, destruction MAY include cryptographic key destruction in addition to physical/object deletion.

---

# 92. Backup interaction

Retention/deletion policy SHALL account for backup copies.

---

# 93. Backup is not archive

A disaster-recovery backup SHALL NOT be used as the primary records archive.

---

# 94. Archive is not backup

An archive preserves records for long-term access/compliance.

It does not substitute for recoverability engineering.

---

# 95. Object versioning

Object-storage versioning MAY be used as a technical protection mechanism.

It SHALL NOT replace application-level evidence/version semantics.

---

# 96. Immutability controls

Where policy requires strong evidence preservation, storage SHOULD support immutable retention controls such as write-once/retention-lock semantics.

---

# 97. Storage lock is not business policy

Infrastructure retention lock SHALL implement approved retention policy; it SHALL not define that policy.

---

# 98. Retention-policy safety

A misconfigured application SHALL not be able to shorten immutable regulatory retention silently.

---

# 99. Storage deletion privilege

Ordinary ERP application credentials SHOULD NOT have unrestricted authority to permanently erase protected archives.

---

# 100. Separation of duties

Where risk requires:

```text
record owner
retention administrator
storage administrator
legal hold administrator
```

SHOULD be distinct roles.

---

# 101. Classification

Documents SHALL inherit or receive explicit information classification.

---

# 102. Classification categories

Baobab's wider classification model SHALL apply, including applicable categories such as:

```text
Public
Baobab-owned/Internal
Tenant-specific
Confidential/Restricted
```

according to the canonical classification specification.

---

# 103. Default classification

ERP financial documents SHALL NOT default to Public.

---

# 104. Classification inheritance

A document MAY inherit classification from:

```text
business record
Tenant
LegalEntity
document type
```

subject to explicit inheritance rules.

---

# 105. Strongest applicable classification

Where multiple rules apply, the stronger restriction SHOULD normally prevail unless policy explicitly specifies otherwise.

---

# 106. Tenant isolation

Every tenant-specific document SHALL remain tenant-isolated.

---

# 107. LegalEntity boundary

Access to one LegalEntity's invoices SHALL not follow merely from corporate group ownership.

---

# 108. Group access

Nabhold group-level access to subsidiary records SHALL require explicit authorization.

---

# 109. Cross-tenant object key attack

Knowing an object key SHALL not grant access.

---

# 110. Object authorization

Authorization SHALL occur independently of storage-key knowledge.

---

# 111. Object key opacity

Storage keys SHOULD be opaque and SHALL not encode sensitive information unnecessarily.

Avoid:

```text
/thamani/customer-john-smith/tax-id/invoice.pdf
```

---

# 112. Context metadata

Where appropriate, document metadata SHALL retain immutable historical:

```text
Tenant
LegalEntity
Market
DigitalEstate
```

Context.

---

# 113. Market access

Market association does not automatically determine access rights.

---

# 114. Residency

Document storage SHALL obey applicable `ResidencyPolicy`.

---

# 115. Residency covers derivatives

Residency policy SHALL apply to:

```text
originals
derivatives
previews
indexes
backups
archives
malware quarantine
```

where they contain protected data.

---

# 116. Cross-region copies

Replication to another region SHALL be treated as data movement.

---

# 117. CDN

ERP evidence SHALL NOT be placed on a public CDN merely for convenience.

---

# 118. Controlled delivery

Customer-accessible documents MAY use controlled edge delivery after authorization.

---

# 119. Customer document access

A customer SHOULD access only documents associated with resources they are authorised to view.

---

# 120. B2B organisation access

B2B document access SHALL respect buyer-organisation membership and document scope.

---

# 121. Employee access

Back-office access SHALL follow least privilege.

---

# 122. Supplier access

Future supplier portals SHALL expose only explicitly authorised supplier-facing records.

---

# 123. Regulatory access

Regulatory submission SHALL use a dedicated adapter/capability rather than granting external authorities broad object-store access.

---

# 124. Document encryption

Protected documents SHALL be encrypted in transit and at rest.

---

# 125. Key management

Encryption-key access SHALL be separated from ordinary document access where practical.

---

# 126. Per-object encryption

More granular encryption MAY be adopted for highly restricted evidence.

---

# 127. Search indexing

Document metadata MAY be indexed for discovery.

---

# 128. Full-text indexing

Full document content SHALL only be indexed where:

```text
classification
privacy
residency
retention
```

permit it.

---

# 129. Search index is a projection

Search SHALL NOT become document authority.

---

# 130. Search deletion

Disposition of a document SHALL propagate to derived indexes according to policy.

---

# 131. AI/vector indexes

Embedding/vectorisation of protected documents is another data copy.

---

# 132. Vector governance

Documents SHALL NOT be sent to AI/vector systems without:

```text
authorization
classification approval
residency compatibility
purpose limitation
```

---

# 133. AI model training

ERP documents SHALL NOT automatically become model-training data.

---

# 134. Intelligence retrieval

The Intelligence Engine MAY retrieve authorised evidence for:

```text
document classification
extraction
reconciliation
analysis
```

through governed APIs.

---

# 135. Intelligence least privilege

Intelligence SHALL receive only documents required for the authorised task.

---

# 136. Audit access

Document reads of sensitive evidence SHOULD be auditable where risk requires.

---

# 137. Audit fields

Access audit MAY include:

```text
principal
workload
Tenant
LegalEntity
document_id
action
timestamp
outcome
reason/purpose where required
```

---

# 138. Download audit

Highly sensitive evidence MAY audit downloads separately from metadata views.

---

# 139. Audit log privacy

Audit logs SHALL not reproduce full document content.

---

# 140. Document events

Document lifecycle events MAY include:

```text
document.created.v1
document.version-added.v1
document.validated.v1
document.superseded.v1
document.archived.v1
document.legal-hold-applied.v1
document.legal-hold-released.v1
```

Final ownership/naming SHALL be defined in `nabhold/shared`.

---

# 141. Binary payload prohibition

Canonical events SHALL NOT carry document binaries.

---

# 142. Event references

Events MAY contain:

```text
document_id
document_type
business_entity_id
classification
```

where authorised.

---

# 143. No permanent object URL in event

Events SHOULD NOT contain long-lived signed/public object URLs.

---

# 144. Retrieval on demand

Consumers SHALL request document access through an authorised document API.

---

# 145. Document API

Conceptual resources MAY include:

```text
/documents
/documents/{id}
/documents/{id}/versions
/documents/{id}/download
/documents/{id}/relationships
/documents/{id}/legal-holds
```

---

# 146. Upload API

Upload SHOULD use an explicit session.

Conceptually:

```text
POST /documents/upload-sessions
```

followed by validation/finalisation.

---

# 147. Direct object upload

Pre-signed direct-to-object-storage upload MAY be used for efficiency.

The application SHALL still govern:

```text
authorization
object destination
size
type
expiry
finalisation
```

---

# 148. Upload completion

Upload completion SHALL not mean the document is trusted.

---

# 149. Validation state

Consumers SHALL distinguish:

```text
uploaded
```

from:

```text
validated
```

---

# 150. Idempotent uploads

Document ingestion SHOULD support idempotency.

---

# 151. Duplicate binary

Two DocumentRecords MAY legitimately reference identical binary content.

---

# 152. Deduplication

Content deduplication MAY be implemented internally.

It SHALL not collapse distinct business records merely because their hashes match.

---

# 153. Hash collision handling

Digest SHALL be used as integrity evidence, not assumed to be infallible identity without appropriate controls.

---

# 154. Attachment relationship

A single artifact MAY support multiple business records where policy allows.

---

# 155. Access intersection

When a document relates to multiple records, authorization SHALL not accidentally broaden access.

---

# 156. Document supersession

Superseding a document SHALL preserve:

```text
old version
new version
reason
actor
time
```

---

# 157. Correction

Corrected invoices SHALL follow financial correction rules before a new final artifact is produced.

---

# 158. No PDF editing as financial correction

Editing a PDF SHALL never correct posted ERP accounting.

---

# 159. Regulatory document generation

Jurisdiction-specific formats SHALL follow ADR-ERP-009.

---

# 160. Machine-readable invoices

Some jurisdictions may require structured formats rather than—or in addition to—PDF.

Baobab SHALL support multiple representations of one business document.

---

# 161. Representation model

Example:

```text
Canonical Customer Invoice
          │
          ├── PDF representation
          ├── XML representation
          └── regulatory JSON representation
```

where applicable.

---

# 162. Multiple representation integrity

Each representation SHALL identify the same authoritative business record.

---

# 163. Regulatory acknowledgement

A regulatory authority's acceptance/rejection response SHALL be retained as separate evidence.

---

# 164. Submission identity

Regulatory submission IDs SHALL be ExternalReferences.

---

# 165. Evidence chain

For regulated invoices:

```text
ERP Invoice
    │
    ▼
Generated Payload
    │
    ▼
Submission
    │
    ▼
Authority Response
    │
    ▼
Acknowledgement Evidence
```

SHALL be reconstructable.

---

# 166. Customs evidence

For import workflows, the evidence chain MAY include:

```text
Purchase Order
Commercial Invoice
Packing List
Bill of Lading
Certificate of Origin
Customs Declaration
Inspection
Material Receipt
Landed-Cost Invoice
```

---

# 167. Cross-document relationship

These artifacts SHALL be linked through business relationships, not filenames.

---

# 168. Shipment document relationship

One bill of lading may relate to:

```text
multiple Purchase Orders
multiple Products
multiple receipts
```

---

# 169. Document graph

Baobab SHOULD support typed relationships sufficient to represent such document graphs.

---

# 170. Document graph is not workflow engine

Relationship metadata SHALL not become an uncontrolled substitute for business workflow.

---

# 171. Contract records

Contracts may require stronger lifecycle controls than ordinary attachments.

---

# 172. Contract version

Signed contract versions SHALL be immutable evidence.

---

# 173. Draft contract

Drafts SHALL remain clearly distinguishable from executed agreements.

---

# 174. Electronic signatures

If electronic signature is introduced, provider-specific signature identifiers SHALL remain external references.

---

# 175. Email evidence

Business email MAY sometimes become evidentiary material.

It SHALL be captured deliberately rather than assuming the entire mailbox is an ERP record repository.

---

# 176. Communication evidence

Relevant communications MAY be attached/linked under explicit retention policy.

---

# 177. Document naming

Human-readable naming MAY aid users.

Identity SHALL remain UUID/reference based.

---

# 178. Naming collisions

Two files named:

```text
invoice.pdf
```

SHALL remain distinct.

---

# 179. Time

Document metadata SHALL distinguish where necessary:

```text
business document date
upload time
creation time
finalisation time
signature time
regulatory submission time
```

---

# 180. Timezone

Machine timestamps SHALL use explicit timezone/UTC conventions.

Business dates SHALL remain distinct.

---

# 181. Chain of custody

High-value evidence SHOULD support reconstructable chain of custody.

---

# 182. Chain-of-custody fields

May include:

```text
captured_by
captured_at
source
digest
validated_by
validation_time
transfers
access
supersession
disposition
```

---

# 183. Evidence export

Evidence export SHALL preserve metadata required to interpret the artifact.

---

# 184. Export manifest

A controlled evidence export SHOULD include a manifest containing:

```text
document IDs
business references
digests
media types
versions
timestamps
```

---

# 185. Export integrity

The manifest itself MAY be signed/digested where stronger evidence is required.

---

# 186. Bulk export

Bulk document export SHALL be:

```text
authorised
bounded
audited
rate-controlled
```

---

# 187. Tenant export

Tenant data export SHALL not include another Tenant's documents.

---

# 188. Divestiture

If a LegalEntity leaves the group, document transfer SHALL follow:

```text
ownership
retention
contract
privacy
regulatory
```

requirements.

Canonical identities SHOULD remain historically resolvable where required.

---

# 189. Tenant offboarding

Offboarding SHALL NOT simply:

```text
DELETE bucket/*
```

---

# 190. Offboarding sequence

Conceptually:

```text
suspend new activity
      │
      ▼
classify records
      │
      ▼
export/transfer where required
      │
      ▼
apply retention/legal holds
      │
      ▼
archive retained evidence
      │
      ▼
destroy eligible data
      │
      ▼
retain disposition audit
```

---

# 191. Engine migration

Moving ERP to another EngineInstance SHALL not require document identity changes.

---

# 192. Storage migration

Moving from one object-store implementation to another SHALL preserve:

```text
Document ID
version ID
digest
relationships
retention metadata
```

---

# 193. Migration verification

Every migrated object SHALL be integrity-verified.

---

# 194. Backup

Document metadata and objects SHALL have coordinated recovery strategy.

---

# 195. Metadata/object mismatch

Baobab SHALL detect:

```text
metadata exists, object missing

object exists, metadata missing

digest mismatch

wrong version

wrong Tenant storage scope
```

---

# 196. Document reconciliation

Document reconciliation SHALL therefore be first-class.

---

# 197. Reconciliation dimensions

At minimum:

```text
existence
digest
size
version
relationship
classification
retention state
legal hold
storage location
```

---

# 198. Orphan object

Orphan objects SHALL be quarantined/investigated before deletion.

---

# 199. Broken reference

Broken business-record references SHALL generate reconciliation findings.

---

# 200. Recovery

After object-storage recovery, document reconciliation SHALL run before declaring evidence services fully recovered.

---

# 201. Point-in-time mismatch

Database and object storage may recover to different effective points.

This SHALL be detected.

---

# 202. Upload transaction boundary

Baobab SHALL NOT pretend PostgreSQL and object storage participate in one ACID transaction.

---

# 203. Durable upload workflow

Instead:

```text
create upload intent
      │
      ▼
upload object
      │
      ▼
validate object
      │
      ▼
commit metadata/finalisation
      │
      ▼
reconcile
```

---

# 204. Failed finalisation

An uploaded object without final metadata SHALL expire/quarantine according to policy.

---

# 205. Failed object upload

A metadata record whose upload never completed SHALL remain incomplete and eventually expire/reconcile.

---

# 206. Observability

ADR-ERP-011 SHALL include document signals such as:

```text
upload failures
scan failures
quarantine backlog
missing objects
digest mismatches
render failures
retention failures
legal-hold errors
object-storage latency/errors
```

---

# 207. Metrics privacy

Filenames, invoice numbers, customer names and document IDs SHALL not become uncontrolled metric labels.

---

# 208. Alerting

Critical alerts SHOULD include:

```text
protected evidence deletion failure
unexpected deletion
legal-hold violation attempt
storage corruption
malware detection
cross-tenant access attempt
```

---

# 209. Security incident

Suspicious documents SHALL be isolated without destroying evidence required for investigation.

---

# 210. Ransomware resilience

Evidence storage SHOULD support controls that reduce the ability of compromised application credentials to destroy historical records.

---

# 211. Disaster recovery

Document DR SHALL preserve:

```text
objects
metadata
retention
legal holds
digests
relationships
```

---

# 212. Recovery priority

Critical statutory/financial evidence MAY receive higher recovery priority than low-value content derivatives.

---

# 213. Restore verification

Restore testing SHALL include actual document retrieval and digest verification.

---

# 214. Non-production restoration

Production evidence SHALL not be copied casually into development environments.

---

# 215. Sanitisation

Where production-derived documents are required for testing, they SHALL be appropriately:

```text
authorised
minimised
masked
synthetic
```

where feasible.

---

# 216. Test documents

Automated tests SHOULD use synthetic evidence rather than real customer/supplier documents.

---

# 217. Repository ownership

`nabhold/shared` SHALL own cross-platform document/evidence contracts.

---

# 218. ERP repository ownership

`nabhold/baobab-erp` SHALL own ERP-specific document relationships and adapters.

---

# 219. Infrastructure ownership

`nabhold/infrastructure` SHALL own deployment of:

```text
object storage
encryption integration
backup infrastructure
retention-lock infrastructure
malware-scanning infrastructure
```

subject to platform contracts.

---

# 220. Control Plane ownership

Control Plane SHALL own applicable:

```text
Context
Tenant
LegalEntity
Market
ResidencyPolicy
IsolationProfile
```

metadata.

It SHALL NOT store all enterprise binaries.

---

# 221. Payload ownership

Payload SHALL own CMS/editorial content assets within its bounded context.

---

# 222. No generic enterprise file dump

Neither Payload nor ERP SHALL become an uncontrolled company-wide network drive.

---

# 223. Dedicated document service

Baobab MAY introduce a dedicated document/evidence capability if cross-engine requirements justify it.

---

# 224. Capability model

Such a service SHALL be registered as:

```text
Engine / Capability
```

or other appropriate canonical platform concept rather than bypassing the Control Plane.

---

# 225. Future document service

A future service MAY provide:

```text
upload
validation
malware scan
object abstraction
versioning
retention
legal hold
rendering
access
evidence export
```

without owning ERP financial state.

---

# 226. Avoid premature service

This ADR does NOT require a new microservice immediately.

The contract may initially be implemented inside the ERP integration boundary plus shared infrastructure.

---

# 227. Extraction pipeline

Future invoice ingestion MAY operate:

```text
Supplier Document
       │
       ▼
Secure Upload
       │
       ▼
Malware Scan
       │
       ▼
Document Classification
       │
       ▼
OCR / AI Extraction
       │
       ▼
Validation
       │
       ▼
Supplier Mapping
       │
       ▼
ERP Draft Invoice
       │
       ▼
Human/Policy Approval
       │
       ▼
ERP Posting
```

---

# 228. Extraction traceability

ERP structured values SHOULD retain provenance back to the source document where useful.

---

# 229. Extraction correction

Correcting an extracted value SHALL not alter the original uploaded evidence.

---

# 230. Duplicate invoice detection

Document digest MAY assist duplicate detection.

It SHALL not be the only control.

---

# 231. Duplicate controls

Supplier invoice duplication MAY consider:

```text
supplier
invoice number
invoice date
amount
currency
digest
```

within explicit scope.

---

# 232. Duplicate does not mean identical binary

Two scans of the same invoice may have different digests.

---

# 233. Evidence authenticity

Document authenticity MAY require verification beyond duplicate detection.

---

# 234. Document lifecycle events

Events SHALL describe semantic lifecycle, not object-store implementation.

Prefer:

```text
document.validated.v1
```

not:

```text
s3.object-put.v1
```

as the canonical business event.

---

# 235. Infrastructure events

Object-store technical events MAY still exist for operational automation.

They SHALL remain infrastructure events.

---

# 236. Document identifiers in APIs

External APIs SHALL use canonical Document IDs.

---

# 237. Storage paths private

Bucket names, internal keys and filesystem paths SHALL not form public API contracts.

---

# 238. Download response

The API MAY return:

```text
temporary redirect
stream
short-lived signed URL
```

according to policy.

---

# 239. Content-Disposition

Downloaded filenames SHOULD be sanitised and safely generated.

---

# 240. Browser security

Customer-facing rendering SHALL use appropriate:

```text
Content-Type
Content-Disposition
CSP
X-Content-Type-Options
```

and related controls.

---

# 241. Active document rendering

HTML or script-capable document types require additional security.

---

# 242. PDF rendering

Generated PDFs SHALL be treated as generated artifacts, not assumed secure merely because of format.

---

# 243. Metadata leakage

PDF/document metadata SHOULD be reviewed to avoid leaking:

```text
internal usernames
filesystem paths
software internals
unnecessary personal information
```

---

# 244. Internationalisation

Documents SHALL support required:

```text
language
locale
number formatting
date formatting
currency formatting
```

without changing underlying canonical financial values.

---

# 245. Translation

Translated rendering SHALL not alter accounting semantics.

---

# 246. Original language

Where legal requirements demand an original-language artifact, that representation SHALL be preserved.

---

# 247. Accessibility

Customer-facing documents SHOULD meet applicable accessibility requirements where practical/required.

---

# 248. Records management invariants

```text
INV-ERP-DOC-001
ERP business state and document binaries are distinct.

INV-ERP-DOC-002
Rendered invoices do not replace ERP accounting authority.

INV-ERP-DOC-003
Attachments do not automatically become master data.

INV-ERP-DOC-004
Payload CMS is not the ERP financial-record authority.

INV-ERP-DOC-005
Binary artifacts are not embedded in canonical events.

INV-ERP-DOC-006
Canonical document identity is independent of object-storage location.

INV-ERP-DOC-007
Object keys are not business identity.

INV-ERP-DOC-008
Cryptographic digests identify content integrity, not business identity.

INV-ERP-DOC-009
ERP documents are private by default.

INV-ERP-DOC-010
Knowing an object key never grants authorization.

INV-ERP-DOC-011
Signed access is short-lived and authorization-gated.

INV-ERP-DOC-012
Untrusted uploads are validated before trusted use.

INV-ERP-DOC-013
Filename extensions do not prove file type.

INV-ERP-DOC-014
Malware controls apply according to document risk.

INV-ERP-DOC-015
Evidence integrity is cryptographically verifiable.

INV-ERP-DOC-016
A digest alone does not prove authenticity.

INV-ERP-DOC-017
Final evidence is not silently overwritten.

INV-ERP-DOC-018
Supersession preserves previous versions.

INV-ERP-DOC-019
Draft and final financial documents remain distinguishable.

INV-ERP-DOC-020
Template systems do not own financial facts.

INV-ERP-DOC-021
AI extraction does not establish financial truth.

INV-ERP-DOC-022
Original evidence survives derived-data correction where retention requires.

INV-ERP-DOC-023
Original and derivative artifacts are distinguishable.

INV-ERP-DOC-024
Retention is policy-driven.

INV-ERP-DOC-025
Engineering does not invent legal retention periods.

INV-ERP-DOC-026
Legal hold overrides ordinary destruction.

INV-ERP-DOC-027
Legal-hold changes are audited.

INV-ERP-DOC-028
Retention expiration means disposition eligibility, not unconditional deletion.

INV-ERP-DOC-029
Backup is not records archive.

INV-ERP-DOC-030
Archive is not disaster-recovery backup.

INV-ERP-DOC-031
Infrastructure retention implements rather than defines business retention policy.

INV-ERP-DOC-032
Tenant-specific documents remain tenant-isolated.

INV-ERP-DOC-033
Corporate ownership does not imply unrestricted subsidiary-document access.

INV-ERP-DOC-034
Residency applies to originals and derived copies.

INV-ERP-DOC-035
Cross-region document replication is governed data movement.

INV-ERP-DOC-036
Protected documents are encrypted at rest and in transit.

INV-ERP-DOC-037
Search indexes are projections, not document authority.

INV-ERP-DOC-038
AI/vector indexes are governed data copies.

INV-ERP-DOC-039
ERP documents do not automatically become AI-training data.

INV-ERP-DOC-040
Sensitive document access is auditable according to risk.

INV-ERP-DOC-041
Document events never expose permanent object-store access.

INV-ERP-DOC-042
Identical binary content does not imply identical business identity.

INV-ERP-DOC-043
Editing a PDF never corrects posted accounting.

INV-ERP-DOC-044
One business document may have multiple authorised representations.

INV-ERP-DOC-045
Regulatory submission identifiers are ExternalReferences.

INV-ERP-DOC-046
Cross-document relationships are explicit.

INV-ERP-DOC-047
Offboarding respects retention and legal hold.

INV-ERP-DOC-048
Engine/storage migration preserves document identity and digest.

INV-ERP-DOC-049
Document metadata and binary objects are reconcilable.

INV-ERP-DOC-050
A database/object-store restore is incomplete until evidence reconciliation succeeds.

INV-ERP-DOC-051
PostgreSQL and object storage are not treated as one ACID transaction.

INV-ERP-DOC-052
Orphaned uploads are safely reconciled.

INV-ERP-DOC-053
Document telemetry avoids sensitive high-cardinality labels.

INV-ERP-DOC-054
Non-production environments do not receive uncontrolled production evidence.

INV-ERP-DOC-055
Shared contracts do not expose storage-provider internals.

INV-ERP-DOC-056
Document services do not become shadow ERP systems.

INV-ERP-DOC-057
Document extraction retains source provenance.

INV-ERP-DOC-058
Duplicate detection never relies solely on filename.

INV-ERP-DOC-059
Canonical document events describe business/document semantics, not storage implementation.

INV-ERP-DOC-060
Records management preserves business truth, evidence integrity, tenant isolation and legal obligations throughout the record lifecycle.
```

---

# 249. Initial production implementation

The initial implementation SHOULD support:

```text
Customer Invoice PDF
Supplier Invoice attachment
Purchase Order PDF
Goods Receipt evidence
Payment evidence
Import/customs attachments
```

with:

```text
private object storage
canonical document ID
business-record relationship
SHA-256 digest
classification
upload validation
malware scanning
version metadata
retention metadata
authorised retrieval
audit
backup
reconciliation
```

---

# 250. Initial import-document scenario

For imported goods, the first end-to-end evidence graph SHOULD support:

```text
Canonical Import Shipment
       │
       ├── Commercial Invoice
       ├── Packing List
       ├── Bill of Lading
       ├── Certificate of Origin
       ├── Inspection Evidence
       ├── Customs Declaration
       ├── Clearing Invoice
       └── Delivery / Receipt Evidence
                 │
                 ▼
             ERP Receipt
                 │
                 ▼
          ERP Landed Cost
```

No filename SHALL serve as the relationship mechanism.

---

# 251. Initial supplier-invoice scenario

```text
Supplier Invoice PDF
       │
       ▼
Secure Upload
       │
       ▼
Quarantine / Scan
       │
       ▼
Digest + Metadata
       │
       ▼
Optional Extraction
       │
       ▼
Party Resolution
       │
       ▼
ERP Draft Supplier Invoice
       │
       ▼
PO / Receipt Matching
       │
       ▼
Approval
       │
       ▼
Posting
       │
       ▼
Evidence Relationship Preserved
```

---

# 252. Initial customer-invoice scenario

```text
ERP Customer Invoice
       │
       ▼
Posted
       │
       ▼
Document Rendering
       │
       ├── ERP facts
       ├── approved template
       ├── LegalEntity identity
       ├── locale
       └── regulatory data
       │
       ▼
Final Artifact
       │
       ▼
Digest
       │
       ▼
Protected Object Storage
       │
       ▼
Customer-authorised Retrieval
```

---

# 253. Definition of done

ADR-ERP-017 SHALL be considered implemented when:

- [ ] ERP Business Record and Document are separate concepts.
- [ ] Attachment and Evidence are separately modelled.
- [ ] canonical Document identity exists where cross-engine use requires it.
- [ ] storage identity is not canonical identity.
- [ ] cryptographic content integrity is implemented.
- [ ] object storage is private by default.
- [ ] authorised short-lived retrieval exists.
- [ ] upload-session architecture exists.
- [ ] quarantine exists for untrusted uploads.
- [ ] file-type validation exists.
- [ ] malware scanning exists according to risk.
- [ ] file-size controls exist.
- [ ] document versions are preserved.
- [ ] original/derived/rendered artifacts are distinguishable.
- [ ] final evidence cannot be silently overwritten.
- [ ] invoice rendering uses authoritative ERP facts.
- [ ] Payload assets cannot modify financial facts.
- [ ] supplier-original documents remain preserved where required.
- [ ] OCR/AI extraction is treated as derived data.
- [ ] extraction provenance exists.
- [ ] retention policies are externally governed.
- [ ] legal hold exists.
- [ ] destruction respects legal hold.
- [ ] disposition is auditable where required.
- [ ] backup and archive responsibilities are distinct.
- [ ] tenant isolation applies to objects.
- [ ] LegalEntity access controls exist.
- [ ] ResidencyPolicy applies to document copies.
- [ ] encryption is enabled.
- [ ] sensitive document access can be audited.
- [ ] document events contain references, not binaries.
- [ ] APIs do not expose permanent object-storage URLs.
- [ ] regulatory representations can coexist.
- [ ] regulatory acknowledgements can be retained.
- [ ] cross-document relationships are typed.
- [ ] evidence export includes integrity metadata.
- [ ] tenant offboarding respects retention.
- [ ] storage migration preserves IDs/digests.
- [ ] document reconciliation exists.
- [ ] object/metadata orphan detection exists.
- [ ] restore verification includes digest checks.
- [ ] production documents are protected from uncontrolled non-production copying.
- [ ] document operational telemetry exists.
- [ ] initial supplier-invoice evidence flow is tested.
- [ ] initial customer-invoice rendering flow is tested.
- [ ] initial import-document graph is tested.

---

# 254. Final architectural position

Baobab SHALL reject:

```text
                     FILES

                       │
                       ▼

               "Put them somewhere"

                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
       ERP DB        Payload       Bucket
```

Instead:

```text
                    BUSINESS FACT
                         │
                         ▼
                      iDempiere
                  Authoritative ERP
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
        Rendering    Relationship   Evidence
            │            │            │
            └────────────┼────────────┘
                         ▼
                  DOCUMENT METADATA
                         │
                         ▼
                 CONTROLLED STORAGE
                 ┌───────┼────────┐
                 ▼       ▼        ▼
              Original Derived  Rendered
                 │       │        │
                 └───────┼────────┘
                         ▼
                Integrity / Retention
                         │
                         ▼
                 Authorised Access
                         │
                         ▼
                Audit / Reconciliation
```

The decisive rule is:

> **The business record proves what the ERP says happened; the evidence architecture proves which artifacts existed, which version was retained, whether its content remained intact, and who was entitled to use it.**

And:

> **Payload manages content; object storage stores bytes; iDempiere owns ERP facts; none of these responsibilities may be silently substituted for another.**

This keeps financial records trustworthy while allowing Baobab to evolve its storage provider, rendering technology, CMS, OCR/AI tooling and even ERP engine without losing documentary identity or evidentiary history.

---

# 255. Consequence for the wider Baobab architecture

This ADR also establishes an important future platform boundary:

```text
Document / Evidence Capability
```

is sufficiently cross-cutting that it **may eventually justify its own Baobab Engine or platform capability**.

That decision SHALL NOT be made merely because several repositories need object storage.

A dedicated capability becomes justified when Baobab requires centrally governed:

```text
evidence lifecycle
retention
legal hold
document rendering
malware scanning
document extraction
signature verification
regulatory evidence
chain of custody
cross-engine document relationships
```

at platform scale.

Until that threshold is reached, the same contracts SHALL be implemented without creating a premature microservice.

---

# 256. Definitive statement

```text
ERP RECORD
    establishes business truth

DOCUMENT
    represents that truth

ATTACHMENT
    supports that truth

EVIDENCE
    preserves proof relevant to that truth

OBJECT STORAGE
    stores the bytes

RETENTION POLICY
    governs how long they survive

CANONICAL IDENTITY
    allows them to survive technological change
```

**None of these concepts is interchangeable.**