## Context

See proposal.md — Why. Production forensics confirmed the pipeline is healthy up to the final Web Push send; delivery fails only because recipients have no subscription. Two client defects (no `pushsubscriptionchange` handling, no recovery after a lost/absent subscription) turned a routine subscription loss into a permanent silent outage, and the DB-only failure record made it invisible for ~2 weeks.

Relevant existing constraints:
- The frontend bundle is env-agnostic; `vapidPublicKey` is fetched from `/config.json` at bootstrap on the main thread (not baked at build). The Service Worker (`src/sw.ts`, `injectManifest`) has no access to `IAppConfig`.
- The VAPID keypair is unchanged (public key stable since 2026-05-16; backend `VAPID_PRIVATE_KEY` matches). Re-subscribing with the same key is valid.
- Backend already has OTel instrumentation; the notification service already records `delivered`/`failed` with a failure reason in the DB.

## Goals / Non-Goals

Goals:
- No permission-granted user stays silently unsubscribed after a browser-side subscription loss.
- Browser-initiated subscription rotation is renewed automatically, even with the app closed.
- A systemic push-delivery failure is detectable operationally within minutes.

Non-Goals:
- Preventing subscription loss from legitimate client actions (PWA uninstall, clearing site data) — that loss is correct Web behavior; only recovery and detection are in scope.
- Changing the hype/proximity delivery filtering (unchanged; now merely observable).
- Server-side creation of subscriptions (impossible — a subscription can only originate in the browser).

## Decisions

- **SW obtains the VAPID key by fetching `/config.json` at runtime, not by build-time baking.** The `pushsubscriptionchange` handler needs `applicationServerKey`, but baking it into the SW would break the env-agnostic bundle. The SW fetches same-origin `/config.json` (cache-first) to read `vapidPublicKey`. Alternative considered: main thread posts the key to the SW via `postMessage` and the SW caches it in IndexedDB — rejected as primary because `pushsubscriptionchange` can fire with no client open, so the SW must be able to self-serve the key.
- **Two complementary recovery paths, not one.** (1) SW `pushsubscriptionchange` renews on browser-initiated rotation (works with app closed). (2) A main-thread "resolve push state" check on app open / settings load re-subscribes when permission is `granted` but `getSubscription()` is `null`. `pushsubscriptionchange` has inconsistent cross-browser firing, so the main-thread path is the safety net that also covers uninstall→reinstall and data-clear cases (which fire no event).
- **Detect systemic failure via a log-based metric on the WARNING delivery-failure log, not a raw OTel counter.** Prior art in this project shows the OTLP collector drops some server metrics for cost and that missing-metric alert policies can 400 an entire prod apply. A log-based metric derived from the structured WARNING log (with `failure_reason` as a label) is cheaper, guaranteed present, and avoids that failure mode. The backend still emits the WARNING log as the single source; the alert is built on the log-based metric in cloud-provisioning.
- **Recovery of already-lapsed users is client-driven and automatic.** No server backfill is possible. Existing users with granted permission re-subscribe on next app open via the main-thread path; users whose permission is not granted get the re-enable affordance. This needs no data migration.
- **Re-registration reuses the existing `Create` RPC and per-browser (user, endpoint) scoping.** A rotated subscription yields a new endpoint → a new row; the old endpoint is reaped by the existing `410 Gone` cleanup on the next send. No new RPC or schema change.

## Risks / Trade-offs

- [`pushsubscriptionchange` is not fired reliably by all browsers] → The main-thread resolve-on-open path is the primary safety net; the SW handler is an optimization for the app-closed case, not the sole mechanism.
- [SW `/config.json` fetch fails offline] → Best-effort with cache-first; renewal retries on the next event/open. Failure never crashes the event.
- [Ratio-based alerts are noisy at low pre-launch volume] → Pair the failure-ratio alert with a minimum-volume guard, and add the absolute "active-subscription starvation" signal so a mass loss is caught even at low counts.
- [Duplicate/aggressive re-subscribe loops] → Gate re-subscribe on a state check (`getSubscription()` null AND permission granted) so it runs once per actual loss, not on every navigation.

## Migration Plan

1. Backend release: WARNING logs + delivery-outcome signal + zero-recipient logs (additive, safe).
2. cloud-provisioning: add the log-based metric + alert policy (mirrors `app-error-log-alerting`).
3. Frontend release: SW `pushsubscriptionchange` handler + main-thread recovery + error surfacing (SW update ships via the existing PWA update flow).
4. Verify: approve a concert for a followed artist and confirm real-device delivery; confirm `push_subscriptions` grows as clients re-subscribe and that a forced failure raises the alert.

Rollback: revert the respective releases; all changes are additive (no schema/proto change), so rollback is clean. A reverted SW still leaves users no worse than today.

## Open Questions

- Exact alert thresholds and evaluation windows (failure ratio %, minimum volume) — tunable operationally after deploy without changing the specs or task breakdown; start conservative.
