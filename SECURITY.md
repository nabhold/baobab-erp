# Security Policy

Report vulnerabilities privately through GitHub Private Vulnerability Reporting. Do not
open a public issue containing exploit details, credentials, personal information, or
tenant data.

## Foundations

- Secrets are injected at runtime and never baked into images or committed.
- GitHub Actions use explicit least-privilege permissions and immutable action SHAs.
- Engine-to-engine traffic must use TLS; sensitive events must also be signed
  (`modules/security`).
- Tenant context fails closed (`modules/context`). Missing, inactive, or contradictory
  context is rejected, never defaulted.
- Cross-tenant access attempts are security events and must be retained in the audit
  trail.
- API credentials are service identities with the narrowest role set possible
  (`modules/identity`); administrator credentials are never used by other engines.
- Production iDempiere instances must use strong administrator credentials, maintain
  encrypted backups, and have tested restoration.
- No engine other than this repository's own services reads or writes the `baobab`
  Postgres schema or iDempiere's own schema (ADR-ERP-001).

## Supported versions

Security fixes are applied to the current release line. Upstream iDempiere
vulnerabilities are handled by updating `upstream.lock.yaml`, rebuilding the image, and
releasing a new Baobab ERP version.

## Secret handling

`.env.example` contains names and deliberately unusable placeholders only. Production
secrets belong in the deployment environment or an approved secret manager.
