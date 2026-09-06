# Cutover

Freeze, drain, final-delta-extraction, and go-live runbooks and scripts for the
production cutover (Phase 25–26): freezing ERPNext writes, draining integrations,
capturing a final backup and delta, running the final import and reconciliation, then
flipping the `CapabilityBinding` from ERPNext to iDempiere. Empty until there is a real
cutover to run. See `../README.md`.
