import frappe
from frappe import _

from baobab_erp.tenancy.context import require_tenant_context


def resolve_native_record(canonical_type: str, canonical_id: str) -> tuple[str, str]:
	context = require_tenant_context()
	row = frappe.db.get_value(
		"Baobab Entity Mapping",
		{
			"tenant_id": context.tenant_id,
			"canonical_type": canonical_type,
			"canonical_id": canonical_id,
			"enabled": 1,
		},
		["erpnext_doctype", "erpnext_name"],
		as_dict=True,
	)
	if not row:
		frappe.throw(_("No active ERPNext mapping exists for this canonical identity."), frappe.DoesNotExistError)
	return row.erpnext_doctype, row.erpnext_name
