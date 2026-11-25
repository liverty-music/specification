## Why

Every release is served to all fans the moment it is pinned: `bump-prod-pin` pushes the new image tag to `main` and ArgoCD syncs it, with no point where the owner can use the new version first. The dev environment is stopped indefinitely, so nothing else gives that chance, and a broken release (a layout collapse, a failed sign-in) reaches everyone. Production needs a way to run the new version beside the current one, reachable only on its own address, and to switch fans over without a single failed request for them.

## What Changes

- By default a new release of the fan API (`fan-api`) and the fan web app (`fan-web`) goes live by itself, so the pin bump is still the deploy. There is no automatic check before fans get it: the first implementation (Argo Rollouts `blueGreen` with a smoke Job, which aborted a failing release) was replaced in task 8.6, and the replacement has no such gate.
- A risky release, or one the owner asks to look at, is held on a preview address of its own (a GitHub pre-release moves only the candidate pin) until the owner promotes or aborts it; the owner looks at it by hand there.
- The settlement payout sweeper moves out of the fan API process into a scheduled workflow in the workflow worker, so no preview, candidate or API rollout carries a payout job (design D10).
- Switching fans to a new release causes no failed request: the mechanism is chosen by measurement (design D1), after the first implementation (Argo Rollouts `blueGreen`) answered 503 for 17 to 25 seconds at promotion.
- The fan web app served from the preview address calls the preview API address, so one preview check covers a new web app together with a new API.
- The fan sign-in application accepts sign-in and sign-out redirects from the preview address, so the owner can sign in on preview with a real passkey.
- The preview API accepts the preview web origin.
- The runbook for releasing gains the default flow, the hold, and the read-only commands an agent runs to inspect a waiting release.

Preview runs against the production database and the production identity provider: whatever the owner does on preview is real data. The owner checks with their own account.

The admin, organizer and reception web apps and their APIs (`admin-console-api`, `organizer-console-api`, `reception-api`) get the same rolling-update treatment as `fan-web` (a hold before a Pod is replaced, drain settings, explicit health checks), because the 503 the measurement found on a release is a property of this cluster's load balancer, not of the fan workloads (design D9). They get no preview address. The event consumer and the jobs keep rolling out as today.

## Capabilities

### New Capabilities

None. Releasing is operations tooling; the spec tree describes product behavior, and the behavior this change adds to the product is the one requirement below.

### Modified Capabilities

- `components/infrastructure/fan/web/global/app-shell`: ADDED requirement. When the fan web app is served from the preview address, it calls the preview API address, and the environment check accepts the preview address as production.

The sign-in redirect addresses, the allowed CORS origin, the routes and the rollout are deployment settings, not product behavior, so they are written in design.md and tasks.md and not as requirements.

## Impact

- cloud-provisioning: the release mechanism for `fan-api` and `fan-web` in the prod overlay only (Argo Rollouts today; a candidate lane with a rolling update, or Rollouts with the Gateway API plugin and `pingPong`, after the measurement of design D1); two public hostnames (DNS, certificate, route) for preview; Zitadel redirect URIs for the fan application; the preview origin added to the fan API's allowed CORS origins; the release runbook.
- frontend: the runtime configuration loader derives the API address from the preview address.
- backend: the settlement payout sweeper moves from the fan API process to a scheduled workflow in the workflow worker (design D10); the use case and its spec do not change. The allowed origins are configuration.
- Dev overlays are unchanged and keep plain Deployments (dev is stopped and its releases do not need a gate).
- The prod database is shared by preview and by the current release for as long as a release waits for promotion, so a migration must stay compatible with the previous release (design.md, Risks). The payout sweeper moved out of the fan API (design D10), so a `fan-api` preview carries no payout job.
