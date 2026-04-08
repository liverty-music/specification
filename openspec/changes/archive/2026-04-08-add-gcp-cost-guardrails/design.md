## Context

The `liverty-music-dev` GCP project currently has no billing budget alerts and no per-API quota overrides. All APIs operate at GCP default quota limits, which are far higher than what the dev workload requires.

The Places API (New) has no free tier; every request is billed at $32/1,000. A single bug in the NATS consumer caused ¥323,198 in 5 days (2026-04-03 to 2026-04-08). Vertex AI Gemini 3 Flash has no free token quota; Google Search Grounding has a 5,000/month free tier that dev usage fits within.

Relevant infrastructure is managed via Pulumi in `cloud-provisioning/src/gcp/`:
- `components/project.ts` — API enablement via `ApiService`
- `components/monitoring.ts` — `MonitoringComponent` (log-based alerts, notification channels)
- `src/gcp/index.ts` — orchestrates all GCP components

## Goals / Non-Goals

**Goals:**
- Cap daily Places API (New) Text Search calls to 20 req/day on dev
- Cap daily Vertex AI GenerateContent calls to 50 req/day on dev
- Alert via email when the dev project billing exceeds 50%/90%/100% of a monthly budget threshold
- All guardrails managed as Pulumi IaC (no manual GCP Console changes)

**Non-Goals:**
- Quota limits for prod environment (prod has legitimate higher usage)
- Programmatic billing killswitch (Pub/Sub → Cloud Functions → disable project billing) — deferred as separate change
- Quota limits for other APIs (Last.fm, MusicBrainz, fanart.tv — not GCP-billed)
- Backend code changes for circuit-breaking or quota-aware retry logic

## Decisions

### Decision 1: Pulumi `gcp.serviceusage.ConsumerQuotaOverride` for quota limits

**Choice**: Use `gcp.serviceusage.ConsumerQuotaOverride` to set per-day limits for Places API and Vertex AI.

**Rationale**: This is the standard Pulumi/Terraform resource for overriding GCP service quotas at the project level. It is declarative, version-controlled, and automatically applied via Pulumi Cloud Deployments on PR merge — no manual GCP Console steps required.

**Alternative considered**: Manual quota override via GCP Console. Rejected because it is not reproducible, not auditable, and would be overwritten if Pulumi ever re-creates the project resource.

**Quota metric identifiers** (from GCP):
- Places API (New): `places.googleapis.com/v1/places_requests` with limit name `PLACES_REQUESTS-DAILY-per-project`
- Vertex AI: `aiplatform.googleapis.com/generate_content_requests` with limit name `generate-content-requests-per-minute-per-project-per-base-model` (note: GCP exposes per-minute quota override; we set a low enough value to effectively cap daily usage)

**Note on Vertex AI quota granularity**: GCP's Vertex AI quota override is per-minute-per-model, not per-day. Setting `overrideValue: 1` (1 req/min) gives an effective ceiling of 1,440 req/day, which is much higher than 50. However, the practical throttle for the CronJob (which runs once/week over ~10 minutes) is the per-minute value. To achieve a meaningful daily cap closer to 50, we set `overrideValue: 5` req/min — the CronJob processes ~203 artists sequentially with 1s throttle between calls, so it will still complete normally while a runaway loop would be throttled at 5 req/min instead of the default 60 req/min.

**Alternative for Vertex AI**: Use `aiplatform.googleapis.com` quota `online-prediction-requests-per-base-model` per-day — this does not exist as an overridable metric in the ConsumerQuotaOverride API. Per-minute is the correct granularity for Vertex AI.

### Decision 2: `gcp.billing.Budget` for billing alerts

**Choice**: Add a `gcp.billing.Budget` resource scoped to `liverty-music-dev` with threshold alerts at 50%, 90%, 100% sending email notifications.

**Rationale**: Billing budget alerts are the earliest warning signal — they fire based on actual charges, independent of which API caused them. Email notification requires no additional GCP infrastructure (no Pub/Sub topic, no notification channel setup). The Pulumi GCP provider supports `gcp.billing.Budget` natively.

**Budget amount**: ¥3,000/month (~$20 USD). This covers normal dev usage (weekly CronJob, occasional manual testing) with comfortable headroom.

**Alternative considered**: Pub/Sub + Cloud Functions killswitch. Deferred — higher implementation complexity and risk of false-positive billing disablement. Budget alert is sufficient for now.

### Decision 3: Placement in `monitoring.ts` vs new component

**Choice**: Add quota overrides and billing budget inline in `src/gcp/index.ts` as standalone resources (not wrapped in a component class).

**Rationale**: These are one-off resources with no reusable pattern across environments — prod intentionally has no quota overrides. A dedicated component would add abstraction without benefit. Inline resources in `index.ts` are consistent with how `PostgresComponent` and `WorkloadIdentityComponent` are already instantiated.

**Alternative considered**: New `CostGuardrailsComponent`. Rejected — the guardrails are dev-only and there is no prod counterpart to justify a reusable abstraction.

## Risks / Trade-offs

- **[Risk] Places API quota blocks legitimate CronJob** → The CronJob processes venues sequentially; dev currently has 544 venues all enriched. New venue additions per CronJob run are typically 0–10 (only when new artists are added). 20 req/day provides ample headroom. Mitigation: monitor first CronJob run after deploy.

- **[Risk] Vertex AI per-minute quota (5 req/min) slows CronJob** → The existing client already throttles at 1 req/second (effectively 60/min). Setting override to 5/min will slow a 203-artist run from ~3 minutes to ~40 minutes. This is acceptable for a dev weekly batch job. Mitigation: document the expected runtime in tasks.

- **[Risk] `ConsumerQuotaOverride` requires `serviceusage.googleapis.com` billing API** → Already enabled in `project.ts`. No additional enablement needed.

- **[Risk] Quota override propagation delay** → GCP quota overrides can take up to 15 minutes to propagate after `pulumi up`. The Places API will not be quota-limited immediately after deploy. Mitigation: this is a one-time deploy-time gap; acceptable.

## Migration Plan

1. Add `gcp.billing.Budget` and `gcp.serviceusage.ConsumerQuotaOverride` resources to `src/gcp/index.ts` (dev-only, guarded by `environment === 'dev'`)
2. Run `make lint` locally to verify TypeScript compiles
3. Commit, push, open PR to cloud-provisioning
4. Merge PR → Pulumi Cloud Deployments automatically runs `pulumi up` for dev
5. Verify in GCP Console: quota overrides visible under IAM & Admin → Quotas; budget visible under Billing → Budgets & Alerts
6. Re-enable Places API (New) in GCP Console (already done as of 2026-04-08)

**Rollback**: Revert the PR and merge → Pulumi removes the quota overrides and budget on next deploy. No state manipulation required.
