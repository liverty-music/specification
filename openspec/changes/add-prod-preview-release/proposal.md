## Why

Every release is served to all fans the moment it is pinned: `bump-prod-pin` pushes the new image tag to `main` and ArgoCD syncs it, with no point where the owner can use the new version first. The dev environment is stopped indefinitely, so nothing else gives that chance, and a broken release (a layout collapse, a failed sign-in) reaches everyone. Production needs a way to run the new version beside the current one, reachable only on its own address, and to switch fans over once the owner has checked it.

## What Changes

- A new release of the fan API (`fan-api`) and the fan web app (`fan-web`) is first served on a preview address of its own, while fans keep being served the previous release. The release rolls out to fans only when the owner promotes it; a release that fails the check is aborted and fans never see it.
- The fan web app served from the preview address calls the preview API address, so one preview check covers a new web app together with a new API.
- The fan sign-in application accepts sign-in and sign-out redirects from the preview address, so the owner can sign in on preview with a real passkey.
- The preview API accepts the preview web origin.
- The runbook for releasing gains a check-then-promote procedure, with the read-only commands an agent runs to inspect a pending release.

Preview runs against the production database and the production identity provider: whatever the owner does on preview is real data. The owner checks with their own account.

Other workloads (admin, organizer and reception web apps and APIs, the event consumer, jobs) keep rolling out as today.

## Capabilities

### New Capabilities

None. Releasing is operations tooling; the spec tree describes product behavior, and the behavior this change adds to the product is the one requirement below.

### Modified Capabilities

- `components/infrastructure/fan/web/global/app-shell`: ADDED requirement. When the fan web app is served from the preview address, it calls the preview API address, and the environment check accepts the preview address as production.

The sign-in redirect addresses, the allowed CORS origin, the routes and the rollout are deployment settings, not product behavior, so they are written in design.md and tasks.md and not as requirements.

## Impact

- cloud-provisioning: Argo Rollouts installed in the cluster; `fan-api` and `fan-web` released through it in the prod overlay only; two public hostnames (DNS, certificate, route) for preview; Zitadel redirect URIs for the fan application; the preview origin added to the fan API's allowed CORS origins; the release runbook.
- frontend: the runtime configuration loader derives the API address from the preview address.
- backend: no code change (the allowed origins are configuration).
- Dev overlays are unchanged and keep plain Deployments (dev is stopped and its releases do not need a gate).
- The prod database is shared by preview and by the current release for as long as a release waits for promotion, so a migration must stay compatible with the previous release (design.md, Risks).
