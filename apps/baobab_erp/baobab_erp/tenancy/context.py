from dataclasses import dataclass

import frappe
from frappe import _
from frappe.exceptions import PermissionError


@dataclass(frozen=True, slots=True)
class TenantContext:
	tenant_id: str
	entity_id: str
	company: str | None


def establish_request_context() -> None:
	"""Resolve context when Baobab headers are present; never invent a default tenant."""
	request = getattr(frappe.local, "request", None)
	if request is None:
		return

	tenant_id = request.headers.get("X-Baobab-Tenant-ID")
	entity_id = request.headers.get("X-Baobab-Entity-ID")
	if not tenant_id and not entity_id:
		return  # Native Desk/API traffic remains governed by Frappe permissions.
	if not tenant_id or not entity_id:
		_log_security_event("incomplete_tenant_context", tenant_id, entity_id)
		raise PermissionError(_("Both tenant and legal-entity context are required."))

	row = frappe.db.get_value(
		"Baobab Tenant Mapping",
		{"tenant_id": tenant_id, "entity_id": entity_id, "status": "Active"},
		["tenant_id", "entity_id", "company"],
		as_dict=True,
	)
	if not row:
		_log_security_event("unresolved_tenant_context", tenant_id, entity_id)
		raise PermissionError(_("Tenant context is not active or does not match the legal entity."))

	frappe.local.baobab_tenant_context = TenantContext(row.tenant_id, row.entity_id, row.company)


def require_tenant_context() -> TenantContext:
	context = getattr(frappe.local, "baobab_tenant_context", None)
	if context is None:
		raise PermissionError(_("A resolved Baobab tenant context is required."))
	return context


def _log_security_event(event: str, tenant_id: str | None, entity_id: str | None) -> None:
	frappe.logger("baobab_security", allow_site=True).warning(
		{"event": event, "tenant_id": tenant_id, "entity_id": entity_id, "user": frappe.session.user}
	)
