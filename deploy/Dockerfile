ARG ERPNEXT_VERSION=v16.33.0
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER root
COPY --chown=frappe:frappe apps/baobab_erp /home/frappe/frappe-bench/apps/baobab_erp
USER frappe

RUN ./env/bin/pip install --no-deps --editable apps/baobab_erp \
 && (grep -qxF baobab_erp sites/apps.txt || printf '\n%s\n' baobab_erp >> sites/apps.txt) \
 && bench build --app baobab_erp
