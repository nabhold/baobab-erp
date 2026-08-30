import frappe
from frappe import _
from frappe.model.document import Document


class BaobabEntityMapping(Document):
	def validate(self) -> None:
		if not frappe.db.exists(self.erpnext_doctype, self.erpnext_name):
			frappe.throw(_("The mapped ERPNext record does not exist."))
		duplicate = frappe.db.exists(
			"Baobab Entity Mapping",
			{
				"tenant_id": self.tenant_id,
				"canonical_type": self.canonical_type,
				"canonical_id": self.canonical_id,
				"name": ["!=", self.name],
			},
		)
		if duplicate:
			frappe.throw(_("This canonical identity is already mapped for the tenant."))
