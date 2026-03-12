## Context

The venue enrichment pipeline runs in the consumer pod as an event handler (`venue.created.v1`) and as a batch step in the concert-discovery CronJob. It queries MusicBrainz first, then falls back to Google Maps. Currently the Google Maps client authenticates via an API key passed as a query parameter, but the key was never provisioned to the consumer pod's environment.

The consumer pod already runs with Workload Identity Federation — the `backend-app` GCP service account is bound to the K8s service account via GKE Workload Identity, and Application Default Credentials (ADC) are available inside the pod. This is used today for Cloud SQL IAM authentication.

Error logging is currently spread across three layers (usecase `enrichOne`, repository `MarkFailed`, event consumer `Handle`), making it difficult to correlate failures in Cloud Logging.

## Goals / Non-Goals

**Goals:**
- Enable Google Maps Places API access using WIF/OAuth (no API key secret management)
- Consolidate enrichment error logs to top-level call sites with full diagnostic attributes
- Keep the enrichment pipeline's existing retry semantics unchanged

**Non-Goals:**
- Re-enriching the 196 currently-failed venues (separate operational task after deployment)
- Improving venue name normalization or deduplication logic
- Migrating from Places API legacy to Places API (New) endpoint format (current Text Search endpoint works with OAuth)

## Decisions

### D1: WIF/OAuth via ADC instead of API key

**Decision:** Use `golang.org/x/oauth2/google` to obtain an OAuth2 token via Application Default Credentials (ADC), and send it as `Authorization: Bearer <token>` with `X-Goog-User-Project` header.

**Alternatives considered:**
- **API key via Secret Manager + ExternalSecret**: Requires new GCP secret, ExternalSecret resource, and key rotation management. More moving parts.
- **API key via Pulumi-managed ConfigMap**: Insecure — API key would be visible in plain text in K8s manifests.

**Rationale:** WIF is already operational for Cloud SQL. Reusing the same SA eliminates secret management entirely. OAuth tokens are short-lived (1h) and auto-refreshed by the `oauth2.TokenSource`, removing rotation concerns.

### D2: Places API Text Search endpoint compatibility with OAuth

**Decision:** Continue using the legacy Text Search endpoint (`/maps/api/place/textsearch/json`) with OAuth Bearer token instead of the `key=` query parameter.

**Rationale:** The Places API (New) documentation confirms OAuth support. The legacy endpoint also accepts OAuth tokens — the authentication method is independent of the endpoint version. This avoids a simultaneous endpoint migration.

### D3: Google Maps searcher always registered (no conditional)

**Decision:** Remove the `if cfg.GoogleMapsAPIKey != ""` conditional in DI wiring. The Google Maps searcher is always registered because ADC is always available in GKE pods with Workload Identity.

**Rationale:** Eliminates a silent failure mode where the searcher was simply absent, causing 60% of venues to fail enrichment without any warning log.

### D4: Error logging consolidation — top-level only

**Decision:** Remove log statements from:
1. `enrichOne()` — searcher transient error warn (L172-175)
2. `VenueRepository.MarkFailed()` — repo-layer warn (L172-175 in venue_repo.go)

Add/enhance log statements at:
1. `EnrichPendingVenues()` — per-venue error log with attrs: `venue_id`, `raw_name`, `admin_area`, `error`, `outcome` (failed/transient)
2. `EnrichOne()` — single error log with same attrs on transient failure
3. `VenueConsumer.Handle()` — error log when `EnrichOne` returns error, with attrs: `venue_id`, `venue_name`, `error`

**Rationale:** A single structured log per venue per enrichment attempt at the top-level call site provides complete context for filtering in Cloud Logging. Internal layers return errors upward; only the outermost handler logs.

### D5: Merge log enhancement (kept in enrichOne)

**Decision:** Keep the merge Info log inside `enrichOne()` (not at the top level) because the merge result data (canonical_id, duplicate_id) is only available inside the function. Enhance it with additional attrs: `canonical_name`, `raw_name`.

**Rationale:** Merge is a success path, not an error path. The top-level caller sees `nil` error and has no merge-specific data to log. Keeping the log at the merge site is the natural location.

## Risks / Trade-offs

**[Risk] Places API not enabled in GCP project** → Pulumi change enables `places-backend.googleapis.com`. Verified via `pulumi preview` before deploy.

**[Risk] IAM permission propagation delay** → IAM bindings can take up to 60s to propagate. Consumer pod restart after Pulumi deploy ensures fresh ADC token. ArgoCD rollout handles this naturally.

**[Risk] OAuth token refresh under load** → `oauth2.TokenSource` from `google.DefaultTokenSource` handles refresh automatically with caching. The MusicBrainz rate limiter (1 req/s) means Google Maps is called at most once per second per venue — well within token refresh capacity.

**[Trade-off] Legacy Text Search endpoint** → We continue using the legacy endpoint rather than migrating to Places API (New) REST format. This is acceptable because the auth change is orthogonal to the endpoint format, and the legacy endpoint is functional.
