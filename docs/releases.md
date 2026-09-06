# Releases

A deployable Baobab ERP release is the composed set described in ADR-ERP-013:

```text
Baobab ERP Release
│
├── iDempiere platform (pinned image, upstream.lock.yaml)
├── Baobab OSGi extensions (idempiere/extensions, versioned in lockstep)
├── Baobab application services (modules/)
├── Database schema expectations (db/migrations, applied and tracked)
└── Deployment manifest (compose.yaml / production orchestration)
```

No production `EngineInstance` is defined merely by a container starting; see
`docs/operations.md` and `architecture/conformance.yaml` for what still needs to be true
first. `CHANGELOG.md` tracks notable changes following Keep a Changelog and Semantic
Versioning; there is no tagged release yet.
