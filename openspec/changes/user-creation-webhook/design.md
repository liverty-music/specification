## Context

Users currently register via Zitadel's hosted registration form. After OIDC callback, the frontend calls the backend `Create` RPC to provision a local user record. The backend extracts identity from validated JWT claims (`sub`, `email`, `name`). This works but only captures minimal profile data — fields like `preferred_language` remain empty despite having DB columns for them.

Zitadel Actions v2 provides an event-driven webhook mechanism that fires on `user.human.added` events with rich profile data including `displayName`, `firstName`, `lastName`, `preferredLanguage`, and `userName`.

The Zitadel instance is hosted on Zitadel Cloud (`dev-svijfm.us1.zitadel.cloud`). Actions v2 requires feature flag activation.

## Goals / Non-Goals

**Goals:**
- Add a Zitadel webhook endpoint that provisions or enriches user records on `user.human.added` events
- Populate `preferred_language` and `name` with richer data from the webhook payload
- Maintain the existing Create RPC as the primary provisioning path (no frontend changes)
- Ensure idempotent handling regardless of which path (RPC or webhook) arrives first

**Non-Goals:**
- Replacing the existing Create RPC flow — it remains the primary mechanism
- Handling other Zitadel event types (email verified, user locked, etc.) — future work
- Real-time push notification to the frontend after webhook processing
- Migrating existing users to backfill preferred_language

## Decisions

### Decision 1: Webhook as complementary path, not replacement

The webhook endpoint runs alongside the existing Create RPC. Both paths write to the same `users` table using `external_id` as the correlation key.

- Create RPC: `INSERT` with `ALREADY_EXISTS` on conflict (existing behavior, unchanged)
- Webhook handler: `UPSERT` — INSERT if user doesn't exist, UPDATE to enrich if user already exists

**Rationale**: Eliminates race condition concerns entirely. The frontend flow doesn't depend on webhook timing. Webhook failures are non-fatal — worst case, the user has less profile data.

**Alternative considered**: Replace Create RPC with webhook-only provisioning. Rejected because of race condition between async webhook and synchronous OIDC callback, and unclear retry guarantees in Zitadel Actions v2.

### Decision 2: Separate HTTP handler, not Connect-RPC

The webhook endpoint is a plain `net/http` handler mounted at `/webhooks/zitadel`, not a Connect-RPC service.

**Rationale**: Zitadel sends a standard HTTP POST with HMAC-signed JSON body. It doesn't speak Connect protocol. The handler needs different auth (HMAC verification vs JWT validation) and different request/response semantics. Keeping it as a plain HTTP handler avoids shoehorning an external integration into the RPC framework.

**Alternative considered**: Create a separate Connect-RPC `WebhookService`. Rejected because Zitadel cannot be configured to speak Connect protocol.

### Decision 3: HMAC signature verification

Verify webhook authenticity using the `ZITADEL-Signature` header with the signing key returned when creating the Zitadel Target.

**Rationale**: Simplest and most reliable option. JWT signing requires JWKS endpoint rotation handling. JWE adds unnecessary encryption complexity for an internal-to-cluster call.

The signing key will be stored in GCP Secret Manager and synced to K8s via External Secrets Operator, consistent with existing secret management patterns.

### Decision 4: UPSERT with COALESCE for enrichment

```sql
INSERT INTO users (external_id, email, name, preferred_language, country, time_zone, is_active)
VALUES ($1, $2, $3, $4, $5, $6, true)
ON CONFLICT (external_id) DO UPDATE SET
  name = COALESCE(NULLIF(EXCLUDED.name, ''), users.name),
  preferred_language = COALESCE(NULLIF(EXCLUDED.preferred_language, ''), users.preferred_language)
RETURNING id
```

**Rationale**: `COALESCE(NULLIF(...))` ensures webhook data only overwrites when it has non-empty values, preventing data loss if the webhook payload is missing fields. This handles both orderings (RPC-first and webhook-first) correctly.

### Decision 5: Adapter layer placement

The webhook handler lives at `internal/adapter/webhook/zitadel_handler.go`, following the existing pattern where `internal/adapter/rpc/` contains Connect-RPC handlers. The `webhook` package is a sibling adapter for HTTP webhook integrations.

### Decision 6: New use case method

Add `UpsertFromWebhook(ctx, params)` to the user use case layer. This is distinct from `Create()` because:
- It uses UPSERT semantics (not INSERT-only)
- It receives pre-validated data from webhook payload (not JWT claims)
- It has different error handling (no `AlreadyExists` error — conflicts are expected)

## Risks / Trade-offs

- **[Zitadel Actions v2 has no documented retry policy]** → Mitigation: The Create RPC remains the primary path. Webhook is best-effort enrichment. Missing webhook data is non-fatal.
- **[Signing key rotation]** → Mitigation: Patching a Zitadel Target regenerates the signing key. Store in Secret Manager with External Secrets Operator for rotation support.
- **[Webhook endpoint exposed to internet]** → Mitigation: HMAC signature verification rejects forged requests. Additionally, the endpoint only performs UPSERT with validated fields — no destructive operations.
- **[Feature flag availability on Zitadel Cloud]** → Mitigation: Verified that Actions v2 is available on Zitadel Cloud via System API feature flag activation.

## Migration Plan

1. Deploy backend with new webhook endpoint (no traffic yet)
2. Enable Actions v2 feature flag on Zitadel Cloud instance
3. Create Zitadel Target (Webhook type) pointing to the backend webhook URL
4. Create Zitadel Execution binding `user.human.added` event to the target
5. Store the Target signing key in GCP Secret Manager
6. Test with a new user registration — verify both Create RPC and webhook fire, and user record is enriched
7. Rollback: Delete the Zitadel Execution to stop webhook delivery. No backend changes needed.

## Open Questions

- Should the webhook endpoint be exposed via the same GKE Gateway ingress or a separate internal-only route? (If Zitadel Cloud needs to reach it, it must be external.)
