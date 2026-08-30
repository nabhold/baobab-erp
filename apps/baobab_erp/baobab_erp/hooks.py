app_name = "baobab_erp"
app_title = "Baobab ERP"
app_publisher = "Nabhold Group Africa"
app_description = "Baobab identity, tenancy, integration, and governance extensions for ERPNext"
app_email = "platform@nabhold.com"
app_license = "GPL-3.0-only"

required_apps = ["erpnext"]

scheduler_events = {
	"cron": {
		"*/5 * * * *": [
			"baobab_erp.integrations.delivery.dispatch_pending_events",
		]
	}
}

before_request = ["baobab_erp.tenancy.context.establish_request_context"]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["module", "=", "Baobab ERP"]],
	},
]
