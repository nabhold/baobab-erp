# Installing the REST API plugin

`RestIdempiereClient` (`modules/integration/idempiere_client.py`) talks to iDempiere's
REST API, provided by the third-party `com.trekglobal.idempiere.rest.api` plugin
([bxservice/idempiere-rest](https://github.com/bxservice/idempiere-rest)). That plugin
is **not** part of the pinned `idempiereofficial/idempiere:13-release` image and is not
built or installed by this repository -- see the gap this closes, and the one it
doesn't, below.

## What's wired up here (verified, not assumed)

`idempiere/Dockerfile` has an install step that runs iDempiere's own, real
plugin-management tooling against whatever p2 repository is dropped at
`idempiere/vendor/rest-api-p2/` at build time:

```sh
${IDEMPIERE_HOME}/update-prd.sh <p2-repository> com.trekglobal.idempiere.rest.api
```

This is confirmed present in the pinned image, not guessed: `update-prd.sh`, its
`director/configuration/` directory, the `org.idempiere.equinox.p2.director.feature`,
and an `org.eclipse.equinox.launcher_1.*.jar` are all shipped inside the official
`idempiereServer13.gtk.linux.x86_64.zip` release
(`idempiere/idempiere-docker`'s `13-release/Dockerfile` unpacks that zip's contents
straight into `$IDEMPIERE_HOME`) -- verified by downloading that exact release archive
from SourceForge and inspecting it directly, not by reading documentation alone. This
is iDempiere's own supported mechanism for installing a plugin's p2 repository into a
running instance (`bxservice/idempiere-rest`'s own README documents the identical
command via its `update-rest-extensions.sh` convenience wrapper); nothing here is
Baobab-specific tooling or a workaround.

If `idempiere/vendor/rest-api-p2/` is empty (its default, tracked state -- see the
`.gitkeep` there), the Dockerfile step detects that and skips cleanly, logging why,
rather than failing the build. Today it is always empty, because producing its
contents is the one step this repository cannot currently do -- see below -- so
`docker build -f idempiere/Dockerfile .` behaves exactly as it did before this file
existed.

## What isn't wired up here, and why

A p2 repository is `content.xml`/`content.jar` + `artifacts.xml`/`artifacts.jar` +
`plugins/` + `features/` directories describing a set of installable OSGi bundles.
Producing one for `com.trekglobal.idempiere.rest.api` means running `mvn verify`
inside `bxservice/idempiere-rest`, built with Eclipse Tycho against a **p2 repository
of iDempiere's own core** (`com.trekglobal.idempiere.extensions.parent/pom.xml`
defaults `idempiere.core.repository.url` to a sibling `../../iDempiere` checkout's own
Tycho build output, `org.idempiere.p2/target/repository`; it can instead be pointed at
a remote p2 site).

Both routes were checked directly against this environment's actual network policy,
not assumed:

- **Pointing at a remote p2 site** (`jenkins.idempiere.org`, the URL
  `bxservice/idempiere-rest`'s own `update-prd.sh` usage example names) is blocked
  here -- the egress proxy returns a policy denial on connect, confirmed via a direct
  request, not inferred from a timeout.
- **Building iDempiere core from source** to produce a local p2 repository is not
  blocked in the same way -- `github.com` (via this session's git-clone proxy),
  `download.eclipse.org`, and `repo1.maven.org` are all reachable -- but it is a large,
  separate Eclipse RCP application build (iDempiere core itself, not this plugin), with
  its own multi-module Tycho target-platform resolution that could still hit a further
  blocked dependency partway through, and was explicitly left out of scope for this
  change (see `architecture/conformance.yaml` against ADR-ERP-005/ADR-ERP-013).

## How to actually produce and install it

1. On a machine/CI runner with network access to build iDempiere core (or to a p2
   mirror of it), either:
   - Clone `idempiere/idempiere` (branch `release-13`, matching `upstream.lock.yaml`'s
     pin) and build `org.idempiere.p2` with Tycho to produce a local p2 repository, or
   - Point `idempiere.core.repository.url` at a p2 site that already has one.
2. Clone `bxservice/idempiere-rest` and run `mvn verify`, setting
   `idempiere.core.repository.url` to whichever repository step 1 produced. This
   produces `com.trekglobal.idempiere.extensions.p2/target/repository/` -- a real p2
   repository for the plugin itself.
3. Copy that repository's contents into `idempiere/vendor/rest-api-p2/` in this repo
   (keeping the `.gitkeep` or not, either is fine) and run
   `docker build -f idempiere/Dockerfile .` (or `docker compose build idempiere`) as
   normal. The install step will find it and run automatically.
4. Confirm the plugin actually started: from the running container,
   `${IDEMPIERE_HOME}/director.sh` or the OSGi console's `ss` command should list
   `com.trekglobal.idempiere.rest.api` as `ACTIVE`. If it shows `STARTING` instead, the
   bundle needs an explicit `sta com.trekglobal.idempiere.rest.api` at the console (a
   known quirk `bxservice/idempiere-rest`'s own README calls out), not a sign the
   install itself failed.

Until this is done, `idempiere` in this repository's runtime has no REST API for
`RestIdempiereClient`'s requests to reach, even though the client itself is real and
spec-verified against a fake server reproducing that exact protocol
(`tests/unit/test_idempiere_client.py`).
