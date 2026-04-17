## Why

Push notification delivery to FCM (`fcm.googleapis.com`) is **completely blocked from inside our GKE clusters** — every webpush call returns HTTP 403 with the body "Your client does not have permission to get URL ... from this server. That's all we know." Direct CLI calls from outside the cluster (Cloud NAT exit) succeed (HTTP 201 Created), proving the VAPID keys, payload encryption, and subscription state are all valid. The bug is purely network-routing.

Root cause traced via official GCP documentation:

- `cloud-provisioning/src/gcp/components/network.ts` configures a private Cloud DNS zone that maps `*.googleapis.com → restricted.googleapis.com (199.36.153.4/30)` for all environments.
- `restricted.googleapis.com` VIP only allows access to **VPC Service Controls-supported** services. Per [VPC-SC supported products](https://cloud.google.com/vpc-service-controls/docs/supported-products), Firebase Cloud Messaging is **not** on that list, so the restricted VIP actively blocks it by design.
- We are not using VPC Service Controls (no `accesscontextmanager` / `ServicePerimeter` resources exist in the codebase). We chose the restricted VIP unnecessarily.

The fix exists in the official Google docs ([configure private google access](https://cloud.google.com/vpc/docs/configure-private-google-access)): use `private.googleapis.com (199.36.153.8/30)` instead, which routes the same `*.googleapis.com` wildcard but **does not enforce VPC-SC allowlisting** and therefore reaches FCM.

Two additional issues surfaced during the investigation and are bundled here because they materially blocked diagnosis:

1. **HTTP error response bodies are universally discarded.** Every outbound HTTP client (`pkg/api/errors.go::FromHTTP`, `webpush/sender.go`, `fanarttv/logo_fetcher.go`) records only the status code on error. Hours of investigation were needed to surface the FCM body "Your client does not have permission ..." that pinpointed the root cause. Future debugging needs that body in logs by default.
2. **`NotifyNewConcerts` debug RPC's success criteria are implicit.** A successful 200 response only means "the pipeline ran"; per-subscription delivery failures are logged separately. The runbook does not state this, leading to false confidence that a 200 means notifications were delivered.

## What Changes

- **Infrastructure (cloud-provisioning)**: Switch the private Cloud DNS zone from `restricted.googleapis.com` (199.36.153.4/30) to `private.googleapis.com` (199.36.153.8/30). DNS zone structure (single `googleapis.com.` zone with wildcard CNAME + A records) and PGA enablement on the subnet remain unchanged. Code comment claiming "PGA has no effect on dev nodes with external IPs" is also corrected — the private DNS zone redirects traffic regardless of node IP status.
- **Backend observability (pkg/api + webpush + fanarttv)**: When an outbound HTTP request returns ≥ 400, capture up to the first 1 KiB of the response body and attach it to the resulting `apperr` as a `slog.Attr`. Apply this to the shared `pkg/api/errors.go::FromHTTP` helper (covers Google Maps, fanart.tv main client, Last.fm, MusicBrainz) plus the two clients with their own error mapping (`webpush/sender.go`, `fanarttv/logo_fetcher.go`).
- **Backend documentation**: Extend `backend/docs/debug-rpc-notify-new-concerts.md` with an explicit "How to verify delivery succeeded" section that names the per-subscription log lines (`RecordPushSend("success" | "gone" | "error")`) and warns that an HTTP 200 RPC response is necessary but not sufficient.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `private-google-access`: VIP changes from restricted to private; rationale, DNS record, and reachability requirements updated. Adds an explicit requirement that FCM (and other non-VPC-SC services) are reachable through the configured VIP.
- `http-retry`: Adds a requirement that error-response body bytes are captured into the resulting `apperr` for diagnostic purposes.

## Impact

- **cloud-provisioning**: change to `network.ts` — DNS A record IPs and CNAME target. Triggers Pulumi rollout to `dev` automatically on merge; staging/prod follow standard manual promotion.
- **backend**:
  - `pkg/api/errors.go` — add body-capture parameter to `FromHTTP`.
  - `internal/infrastructure/webpush/sender.go` — read body before wrapping error.
  - `internal/infrastructure/music/fanarttv/logo_fetcher.go` — same.
  - `backend/docs/debug-rpc-notify-new-concerts.md` — runbook extension.
  - All callers of `FromHTTP` continue to work unchanged (helper does the body read internally).
- **Operational rollout (per-environment validation)**: deploy to dev first → smoke-test FCM via the existing `NotifyNewConcerts` debug RPC + verify pod-internal `curl fcm.googleapis.com/...` no longer returns the "permission" 403 → promote to staging → smoke-test again → promote to prod. Risk: low (private VIP is documented as supporting `*.googleapis.com` wildcard); rollback is a one-line CNAME revert.
- **No proto / no client breaking changes** — purely infra + observability internals.
