# Security Policy

Report vulnerabilities privately through GitHub Private Vulnerability Reporting. Do not open a public issue containing exploit details, credentials, personal information, or tenant data.

## Foundations

- Secrets are injected at runtime and never baked into images or committed.
- GitHub Actions use explicit least-privilege permissions and immutable action SHAs.
- Engine-to-engine traffic must use TLS; sensitive events must also be signed.
- Tenant context fails closed. Missing, inactive, or contradictory context is rejected.
- Cross-tenant access attempts are security events and must be retained in the audit trail.
- API credentials are service identities with the narrowest Frappe roles and permissions possible.
- Production sites must disable developer mode, use strong administrator credentials, maintain encrypted backups, and test restoration.

## Supported versions

Security fixes are applied to the current release line. Upstream Frappe/ERPNext vulnerabilities are handled by updating `upstream.lock.yaml`, rebuilding the image, running compatibility tests, and releasing a new Baobab ERP version.

## Secret handling

`.env.example` contains names and deliberately unusable placeholders only. Production secrets belong in the deployment environment or an approved secret manager. Frappe encryption keys and site configuration must be backed up independently from the database.
