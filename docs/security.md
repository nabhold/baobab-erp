# Security

See `SECURITY.md` at the repository root for the vulnerability-reporting policy. This
page covers the security architecture referenced there (ADR-ERP-010).

## Chain

```text
Identity
   ↓
Authentication (approved platform IdP; not this repository's concern)
   ↓
Trusted Principal (modules/identity.ServiceIdentity)
   ↓
Baobab Context (modules/context, fails closed)
   ↓
Capability Authorization (Control Plane CapabilityBinding)
   ↓
Canonical Mapping (modules/mapping, fails closed)
   ↓
iDempiere native authorization (AD_Role / AD_Client / AD_Org)
```

## Fail-closed rules

- `modules/context.resolve_context` raises `ContextResolutionError` on a missing,
  incomplete, or unresolved tenant/entity pair. It never falls back to a default tenant.
- `modules/mapping.resolve_to_native` / `resolve_to_canonical` raise
  `MappingNotFoundError` rather than guessing by display name or lazily creating a native
  record.
- `modules/inbox.receive` rejects an inbound event whose signature does not verify
  (`InvalidSignatureError`) before the envelope is even parsed for business fields.

## Cross-tenant access

A resolved context for one tenant must never satisfy a request scoped to another; this is
tested explicitly in `tests/tenancy/test_context_resolver.py`
(`test_cross_tenant_pair_fails_closed`). A cross-tenant access attempt is a security event
requiring audit retention, not merely a denied request.
