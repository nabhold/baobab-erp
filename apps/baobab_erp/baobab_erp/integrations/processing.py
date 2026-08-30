import frappe


def process_inbox_event(inbox_name: str) -> None:
	"""Dispatch point for versioned Trade and Pulse event handlers."""
	doc = frappe.get_doc("Baobab Event Inbox", inbox_name)
	if doc.status == "Processed":
		return
	try:
		# Domain handlers are registered here as their contracts are approved.
		doc.status = "Processed"
		doc.processed_at = frappe.utils.now_datetime()
		doc.save(ignore_permissions=True)
	except Exception:
		doc.status = "Failed"
		doc.last_error = frappe.get_traceback()[-2000:]
		doc.save(ignore_permissions=True)
		raise
