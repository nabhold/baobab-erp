# Extension Feature Groupings

Reserved for a p2/OSGi feature definition that groups the `idempiere/extensions/`
bundles into a single installable unit once there are enough of them to warrant it. With
four bundles, `idempiere/Dockerfile` copying each jar into the plugins directory directly
is simpler and equally correct; do not add feature/repository machinery ahead of the need
described in ADR-ERP-013.
