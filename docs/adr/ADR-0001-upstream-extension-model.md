# ADR-0001: Extend, Do Not Fork, Frappe and ERPNext

- Status: Accepted
- Date: 2026-08-30

## Context

Baobab ERP needs platform-specific tenancy, identity, mappings, and integrations while retaining upstream compatibility.

## Decision

Install pinned upstream Frappe and ERPNext releases through Bench. Implement Baobab behaviour exclusively in the `baobab_erp` app using supported hooks, DocTypes, permissions, APIs, fixtures, and patches. Do not vendor or edit upstream source.

An upstream fork requires a separate ADR demonstrating that configuration, hooks, composition, and an upstream contribution cannot satisfy the requirement.

## Consequences

Upgrades remain practical and Baobab code stays reviewable. Some changes may require contribution upstream rather than a quick local edit—which is a useful restraint, not an inconvenience.
