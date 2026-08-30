"""Identity integration seam.

Authentication remains Frappe's responsibility. This module translates an authenticated
Frappe User into canonical Baobab membership context once the canonical identity contract
is published by nabhold/shared. It intentionally does not create a competing password store.
"""

import frappe


def current_actor() -> dict[str, str]:
	return {"frappe_user": frappe.session.user}
