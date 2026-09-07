#!/usr/bin/env bash
# Periodic scheduler for application.dispatch_worker (ADR-ERP-006). The worker itself
# stays a one-shot process by design -- see its own module docstring -- so scheduling
# policy lives here, in deployment configuration, not in the worker's Python code. A
# failed tick is logged and retried on the next tick rather than crashing the loop:
# dispatch_worker.py's own retry/backoff logic (outbox.service.backoff_seconds) already
# governs individual event delivery; this loop only governs how often it gets a turn.
set -euo pipefail

interval="${BAOBAB_DISPATCH_INTERVAL_SECONDS:-60}"

while true; do
  if ! python -m application.dispatch_worker; then
    echo "dispatch_worker tick failed; retrying in ${interval}s" >&2
  fi
  sleep "${interval}"
done
