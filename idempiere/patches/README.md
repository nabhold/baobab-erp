# Upstream Patches — Policy

This directory is intentionally empty.

Per ADR-ERP-004, Baobab does not maintain a long-lived fork of iDempiere core. A patch to
upstream source may be proposed only after an ADR demonstrates that no supported extension
mechanism (OSGi bundle, event handler, model validator, web service, configuration) can
satisfy the requirement, and that an upstream contribution is not a viable near-term path.

If such an ADR is ever accepted, the patch lands here as a versioned `.patch` file named
`NNN-short-description.patch`, referencing the ADR and the exact upstream commit/tag it
applies against, applied in `idempiere/Dockerfile` before the extension bundles are copied
in.
