import frappe


@frappe.whitelist(allow_guest=True, methods=["GET"])
def live() -> dict[str, str]:
	"""Process liveness only; deliberately does not disclose site internals."""
	return {"status": "ok", "service": "baobab-erp"}


@frappe.whitelist(allow_guest=False, methods=["GET"])
def ready() -> dict[str, str]:
	"""Authenticated readiness probe including database connectivity."""
	frappe.db.sql("SELECT 1")
	return {"status": "ready", "service": "baobab-erp"}
