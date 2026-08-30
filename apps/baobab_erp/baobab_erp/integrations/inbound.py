import json

import frappe
from frappe import _

from baobab_erp.integrations.envelope import EventEnvelope
from baobab_erp.integrations.signing import verify_signature


@frappe.whitelist(allow_guest=True, methods=["POST"])
def receive() -> dict[str, str]:
	"""Receive a signed, idempotent engine event and enqueue domain processing."""
	body = frappe.request.get_data(cache=True)
	signature = frappe.get_request_header("X-Baobab-Signature") or ""
	secret = frappe.conf.get("baobab_event_signing_secret") or ""
	if not verify_signature(body, signature, secret):
		frappe.throw(_("Invalid event signature."), frappe.AuthenticationError)

	envelope = EventEnvelope.from_dict(json.loads(body))
	existing = frappe.db.exists("Baobab Event Inbox", {"event_id": envelope.event_id})
	if existing:
		return {"status": "accepted", "event_id": envelope.event_id}

	doc = frappe.get_doc(
		{
			"doctype": "Baobab Event Inbox",
			"event_id": envelope.event_id,
			"event_type": envelope.event_type,
			"schema_version": envelope.schema_version,
			"source_engine": envelope.source,
			"correlation_id": envelope.correlation_id,
			"tenant_id": envelope.tenant_id,
			"entity_id": envelope.entity_id,
			"payload_json": json.dumps(envelope.payload, separators=(",", ":"), sort_keys=True),
			"status": "Received",
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.enqueue("baobab_erp.integrations.processing.process_inbox_event", inbox_name=doc.name)
	return {"status": "accepted", "event_id": envelope.event_id}
