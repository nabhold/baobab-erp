import frappe
from frappe import _
from frappe.model.document import Document


class BaobabTenantMapping(Document):
	def validate(self) -> None:
		self.tenant_id = self.tenant_id.strip()
		self.entity_id = self.entity_id.strip().upper()
		if frappe.db.exists(
			"Baobab Tenant Mapping",
			{"tenant_id": self.tenant_id, "name": ["!=", self.name]},
		):
			frappe.throw(_("Tenant ID must be unique."))
		if frappe.db.exists(
			"Baobab Tenant Mapping",
			{"entity_id": self.entity_id, "name": ["!=", self.name]},
		):
			frappe.throw(_("Legal entity is already mapped to a tenant."))
