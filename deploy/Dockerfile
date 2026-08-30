ARG ERPNEXT_VERSION=v16.33.0
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER root
COPY --chown=frappe:frappe apps/baobab_erp /opt/baobab_erp
USER frappe

RUN bench get-app --skip-assets file:///opt/baobab_erp \
 && bench build --app baobab_erp \
 && rm -rf /opt/baobab_erp
