# PostHog project setup runbook

How to provision a PostHog Cloud EU project for a new Liverty Music environment,
configure it to match our analytics architecture, and wire the Project token
into the per-env Kubernetes ConfigMaps.

This runbook is the operational counterpart to the [`introduce-analytics-tool`](../../openspec/changes/introduce-analytics-tool/proposal.md)
OpenSpec change. Run it once per environment when first standing up that env's
PostHog integration. The current state at the time of writing: **prod** and
**dev** projects exist; **staging** will be provisioned when the staging cluster
is built.

## 1. Sign-up + organisation

Only required the first time, when the Liverty Music PostHog organisation does
not yet exist.

- **Region: European Union** at [`eu.posthog.com`](https://eu.posthog.com).
  Japan ↔ EU has APPI Article 28 adequacy designation since January 2019; Japan
  ↔ US does not, which would force per-user explicit cross-border consent
  capture for every event. Region is fixed at sign-up and **cannot be
  migrated** afterwards — the choice is one-way.
- Organisation name: `Liverty Music` (one organisation across all envs).

## 2. Plan selection

Select **Pay-as-you-go** (not Free).

- The Free plan caps at **1 project**, which is incompatible with the
  per-env separation policy (one PostHog project per Liverty Music
  environment).
- Both plans share the same monthly free tier (1M events / 5K session
  recordings). Pay-as-you-go starts at **$0/month** and only bills on
  overage, so within nominal traffic the effective cost is identical to
  Free.
- On traffic spikes, Free silently drops events past the cap; Pay-as-you-go
  preserves data and bills the overage — preferred for trust-commitment
  posture (no silent data loss).

After signup, immediately set per-product billing limits (Organisation
settings → Billing → Spending controls):

| Product | Hard cap | Rationale |
| --- | --- | --- |
| Product Analytics | **$20/month** | Only actively-used product. $20 covers ~80M events above the 1M free tier — generous headroom while bounding runaway-bug cost. This is an org-level cap sized for prod traffic; dev and staging have negligible traffic and will naturally stay within it. |
| Session Replay | **$0** | Disabled at SDK level and project level (see §4). Cap-at-zero locks accidental enablement out. |
| Feature Flags | **$0** | `IAnalyticsService.getFeatureFlag` is wired but no flags are evaluated yet. Bump only when an actual flag goes into rollout. |
| Experiments | **$0** | Not used. |
| Surveys | **$0** | Not used. |
| Data Warehouse | **$0** | Not used. |
| Logs | **$0** | Not used. The default 50GB free tier disappears fast under accidental high-volume log ingestion. |
| PostHog AI | **$0** | Not used. The default $150 cap PostHog auto-applies is far too generous for our scope. |

These are HARD limits (ingestion stops at the threshold). Set an additional
email alert at ~50% of each cap via Organisation settings → Notifications so
problems surface before they hit the cap.

## 3. Per-environment project

One PostHog project per Liverty Music environment, named `liverty-music-<env>`.
Each project has its own Project token (`phc_…`) and event quota.

- `liverty-music-prod` — production
- `liverty-music-dev` — development (optional; can be created lazily when dev
  runtime comes back online)
- `liverty-music-staging` — staging (lazy; create only when staging runtime
  is provisioned)

Distinct projects per env keep the event streams isolated — production dashboards
never include dev test data, and a dev bug emitting 10x events cannot exhaust
the prod quota.

## 4. Project-level configuration (defense-in-depth)

Each project's **Settings → Project** has feature toggles that gate the SDK
remotely. We rely on the SDK-side configuration in
[`frontend/src/lib/analytics/analytics-service.ts`](https://github.com/liverty-music/frontend/blob/main/src/lib/analytics/analytics-service.ts)
as the primary control (`autocapture: false`, `capture_pageview: false`,
`disable_session_recording: true`, etc.), but the project-level toggles act as
defense-in-depth — they block ingestion even if a future SDK config drift
re-enables the feature.

Set **all of the following toggles OFF** on every project (dev, staging, prod):

| Setting | State | Reasoning |
| --- | --- | --- |
| Autocapture frontend interactions | OFF | Our typed catalogue (`frontend/src/services/analytics-events.ts`) enforces `Events.X` + `EventProps<E>` at compile time. Autocapture bypasses this and captures user-entered DOM text as event props — PII leak risk. SDK-side `autocapture: false` is the primary defense; project-level OFF is belt-and-suspenders. |
| Heatmaps | OFF | Coupled with autocapture (data source). Mouse-move / scroll batches blow through the 1M events/month free tier without contributing to catalogue funnels. |
| Web vitals autocapture | OFF | LCP / INP are valuable signals but emit as `$web_vitals` side-channel events, outside the typed catalogue. If we want them later, integrate via a typed `AnalyticsService.captureWebVital(...)` method so the single-source-of-truth architecture stays intact. |
| Session Replay | OFF | PII redaction prerequisites (introduce-analytics-tool Section 8 tasks 8.1–8.3: input masking, `data-pii` tagging, `.ph-no-capture` on payment + ZK regions) are not yet implemented. Recording without redaction would capture form inputs / addresses / ZK proof entry / ticket QR as raw video — PII leak. Also contradicts the consent screen's "anonymous, aggregated" framing. Revisit once Section 8 tasks ship. |

## 5. Project token handoff

The Project token is a public identifier (PostHog labels it "Write-only key for
use in client libraries. Safe to use in public apps."). Analogous to a Stripe
publishable key — it ends up in the frontend bundle anyway, so direct ConfigMap
embed is appropriate and routing through GCP Secret Manager would add no
security value (only complexity and rotation latency).

Copy the token from **Settings → Project token & ID** into two files per env:

- **Backend**: `cloud-provisioning/k8s/namespaces/backend/overlays/<env>/consumer/configmap.env`

  Add the line:

  ```env
  POSTHOG_PROJECT_API_KEY=phc_…
  ```

- **Frontend**: `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/configmap.yaml`

  Add the JSON field:

  ```jsonc
  "posthogProjectKey": "phc_…",
  ```

The Personal API Key (Account settings → Personal API keys) is a different
credential, used for definitions sync and administrative operations. If/when
introduced into the workflow, it WOULD warrant GSM routing — it grants
write-access to the project.

## 6. Verify

After ConfigMap merge → ArgoCD sync → backend pod restart, the next eligible
user action (e.g. a new user signup, an artist follow) should land as a
catalogue event in PostHog within ~1 minute. Look for `user.created` in the
PostHog `liverty-music-<env>` project's **Activity** tab.

The PostHog UI's "Waiting for events" indicator on the Setup page turns green
once the first event arrives.

## 7. Adding a new environment

When a new env (e.g. staging) is provisioned later:

1. Create a new project `liverty-music-<env>` in the existing organisation
   (left sidebar project switcher → "+ Create project").
2. Repeat §4 (project-level toggles all OFF) on the new project.
3. Copy the Project token and add it to the env's backend `consumer/configmap.env`
   and frontend `configmap.yaml` per §5.
4. Open a single PR with both files; ArgoCD sync activates the integration on
   the next env-cluster reconciliation.

Billing limits set in §2 apply to the organisation as a whole — no per-project
configuration needed.
