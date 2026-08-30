import frappe


def dispatch_pending_events() -> None:
	"""Scheduler seam for bounded, retryable outbox delivery."""
	for name in frappe.get_all(
		"Baobab Event Outbox",
		filters={"status": ["in", ["Pending", "Retry"]]},
		pluck="name",
		limit_page_length=100,
	):
		frappe.enqueue("baobab_erp.integrations.delivery.deliver_event", outbox_name=name)


def deliver_event(outbox_name: str) -> None:
	"""Delivery transport is intentionally deferred until endpoint policy is approved."""
	doc = frappe.get_doc("Baobab Event Outbox", outbox_name)
	if doc.status == "Delivered":
		return
	doc.attempts = (doc.attempts or 0) + 1
	doc.status = "Retry"
	doc.last_error = "No approved destination transport configuration"
	doc.save(ignore_permissions=True)
