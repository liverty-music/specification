## 1. Database Layer

- [ ] 1.1 Add UPSERT query to `UserRepository` — `INSERT ... ON CONFLICT (external_id) DO UPDATE SET name = COALESCE(NULLIF(EXCLUDED.name, ''), users.name), preferred_language = COALESCE(NULLIF(EXCLUDED.preferred_language, ''), users.preferred_language) RETURNING id`
- [ ] 1.2 Add `Upsert(ctx, params) (*entity.User, error)` method to `UserRepository` and `entity.UserRepository` interface

## 2. Use Case Layer

- [ ] 2.1 Add `UpsertFromWebhook(ctx, params *entity.NewUser) (*entity.User, error)` method to user use case
- [ ] 2.2 Add structured logging for webhook-triggered upserts (distinguish from RPC-triggered creates)

## 3. Webhook Handler

- [ ] 3.1 Define Zitadel webhook event payload structs (ZitadelEvent, EventPayload) in `internal/adapter/webhook/`
- [ ] 3.2 Implement HMAC signature verification middleware using `ZITADEL-Signature` header
- [ ] 3.3 Implement `ZitadelWebhookHandler` HTTP handler — parse event, filter for `user.human.added`, call `UpsertFromWebhook`
- [ ] 3.4 Add webhook signing key to backend configuration (`pkg/config/`)

## 4. HTTP Server Integration

- [ ] 4.1 Mount `/webhooks/zitadel` route on the existing HTTP server (alongside Connect-RPC mux)
- [ ] 4.2 Wire `ZitadelWebhookHandler` with user use case dependency injection

## 5. Secret Management & Infrastructure

- [ ] 5.1 Add `zitadel-webhook-signing-key` secret to GCP Secret Manager via Pulumi (`cloud-provisioning`)
- [ ] 5.2 Add ExternalSecret resource to sync signing key to K8s backend namespace
- [ ] 5.3 Add signing key env var to backend Deployment manifest

## 6. Zitadel Configuration

- [ ] 6.1 Enable Actions v2 feature flag on Zitadel Cloud instance
- [ ] 6.2 Create Zitadel Target (Webhook type) pointing to backend `/webhooks/zitadel` endpoint
- [ ] 6.3 Create Zitadel Execution binding `user.human.added` event to the target
- [ ] 6.4 Store the returned signing key in GCP Secret Manager

## 7. Testing

- [ ] 7.1 Unit test: HMAC signature verification (valid, invalid, missing)
- [ ] 7.2 Unit test: Webhook handler event parsing and filtering
- [ ] 7.3 Unit test: UPSERT repository method (insert new, update existing, empty value handling)
- [ ] 7.4 Integration test: End-to-end webhook → UPSERT flow with test HTTP server
