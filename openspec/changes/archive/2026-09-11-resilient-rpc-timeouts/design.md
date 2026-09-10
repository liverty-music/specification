## Context

See proposal.md — Why. This design records the measured request-path budget that justifies a single short client deadline, and how the value is wired.

Measured timeout layers, browser → Go server:

```
Browser client            ← THIS CHANGE (currently unbounded)
  │  Cloudflare = DNS-only (proxied:false) → no proxy timeout
  ▼
GCP External ALB          fan-api: 150s (GCPBackendPolicy)
  │                       admin/organizer console API: GCP default 30s (no policy)
  ▼  no Envoy/Istio; fan-api = 2 replicas always-on (no KEDA scale-to-zero on API path)
http.TimeoutHandler       default 30s / ConcertService 120s
  ▼                       (http.Server ReadTimeout 1s, no WriteTimeout)
downstream                Gemini 120s (observed 25–110s) / DB (bounded by handler)
```

Two facts collapse the earlier "per-method timeout policy" idea into a single default:

1. All frontend RPCs are unary and, in practice, sub-second. The only legitimately long backend op (`ConcertService.SearchNewConcerts`, 120s Gemini) is **not called from any frontend app** (verified by a cross-app grep across fan-web/admin/organizer).
2. Connect-ES v1 already composes the caller's `AbortSignal` with the deadline internally, so the "combine signals with `AbortSignal.any`" technique the motivating blog post recommends is not something we need to hand-roll.

The single call deadline is created once at the call boundary and shared across the interceptor chain — the auth-retry silent-refresh round-trip ([connect-error-router.ts](../../../../frontend/src/services/connect-error-router.ts)) and the generic-retry `Unavailable` backoff (200+400+800 ms). This is why the exact value matters (see Decisions).

## Goals / Non-Goals

**Goals:**
- Bound every frontend RPC with a single default client deadline, applied at the shared transport, no call-site changes.
- Make the value runtime-tunable per environment (via `/config.json`) with a safe built-in fallback.
- Bound the two unbounded Service-Worker `fetch()` calls so slow responses fail closed into existing recovery paths.

**Non-Goals:**
- Per-method / per-service timeout overrides (no frontend call needs one today; add later if that changes).
- Hand-rolled `AbortSignal.any` composition (Connect owns it).
- Any change to the existing 5s `/config.json` bootstrap fetch timeout.
- Backend / `cloud-provisioning` timeout fixes (recorded in proposal Impact as a separate track).

## Decisions

**D1 — Single `defaultTimeoutMs = 10s` on the shared transport, no per-method override.**
Set `defaultTimeoutMs` on `createConnectTransport` in [grpc-transport.ts](../../../../frontend/src/services/grpc-transport.ts). Since all frontend RPCs are fast and none is legitimately long, one value covers every app. Alternatives considered: (a) per-method policy — rejected as over-engineering given no long call exists; (b) no default, opt-in short timeouts per call — rejected because "forgot to set one" silently reverts to today's unbounded hang, whereas a default fails closed.

**D2 — 10s value, accepting the re-auth tail.**
The deadline must also cover a silent token refresh + retried attempt on the `Unauthenticated` path. 10s is chosen for crisp UX (real ops are sub-second; 10s already reads as "something is wrong"). The trade-off: on a slow mobile network, a 401 that triggers `signinSilent()` + retry could rarely exceed 10s and surface as a false `DeadlineExceeded` instead of self-healing. This is accepted because oidc-client-ts pre-emptively renews tokens in the background, so hitting the auth-retry path is already the exception. 15s was considered (comfortably swallows the re-auth tail) but rejected in favor of responsiveness; the runtime-config knob (D3) lets us raise it without a rebuild if telemetry shows re-auth-tail false timeouts.

**D3 — Value sourced from `/config.json` with a built-in 10s fallback.**
Add an optional numeric field (e.g. `rpcTimeoutMs`) to the `AppConfig` type and validation in [app-config.ts](../../../../frontend/shared/config/app-config.ts), defaulting to 10000 when absent. This mirrors the backend's env-configurable timeout convention and matches the existing runtime-config pattern (per-env values served from a ConfigMap). The field is additive and optional, so it does not alter any existing `frontend-runtime-config` scenario and needs no delta there. Alternative: a compile-time constant — rejected because it couples tuning to a rebuild/redeploy.

**D4 — Service-Worker fetches use `AbortSignal.timeout()` directly (no `any`).**
Neither SW fetch has a caller signal to compose with, so a plain `AbortSignal.timeout()` suffices:
- `sendInteraction` (→ PostHog) in [notification-interaction.ts](../../../../frontend/src/lib/analytics/notification-interaction.ts): ~10s. On abort, the existing `throw` → stash → Background-Sync resend path (keyed by the reused `$insert_id`) already handles it; the timeout simply makes a *slow* response take that same path instead of being lost.
- `readVapidPublicKeyCacheFirst` cache-miss branch in [push-renewal.ts](../../../../frontend/src/lib/push/push-renewal.ts): ~5s. Already wrapped in try/catch → returns `null` (skip renewal, retry later), so the timeout only tightens the failure window.

## Risks / Trade-offs

- **Re-auth tail false timeout** → 10s could rarely fire during `signinSilent()` + retry on a slow network, turning a recoverable 401 into a visible error. Mitigation: background token pre-renewal makes this path rare; D3 knob allows raising the value from config without a rebuild; validate against RPC-duration p99 (incl. auth-retry) in OTel post-ship.
- **Unavailable retry squeezed by the shared budget** → the 1.4s total backoff eats into the 10s; a burst of `Unavailable` may exhaust the deadline before all 3 retries run. Accepted: fast ops leave ample headroom, and exhausting into `DeadlineExceeded` is the intended fail-closed outcome.
- **Config field typo / bad value** → a malformed `rpcTimeoutMs` should not break bootstrap. Mitigation: validate as an optional positive number and fall back to 10s on absence/invalid, consistent with existing `AppConfig` validation.
- **Analytics timeout too aggressive** → a legitimately slow-but-succeeding PostHog capture gets aborted and resent, risking duplicate ingestion. Mitigation: resend reuses the same `$insert_id`, which PostHog de-duplicates server-side.
