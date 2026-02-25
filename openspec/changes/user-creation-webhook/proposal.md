## Why

The current user provisioning flow relies entirely on the frontend calling the `Create` RPC after OIDC callback. This means the backend only receives minimal user data available in JWT claims (sub, email, name). Zitadel's `user.human.added` event payload contains richer profile data (preferredLanguage, displayName, firstName, lastName) that we already have DB columns for but cannot populate. By adding a Zitadel Actions v2 webhook as a complementary provisioning path, the backend can capture richer user data at registration time while maintaining the existing frontend-driven flow as the primary mechanism.

## What Changes

- Add a new webhook HTTP endpoint on the backend to receive Zitadel Actions v2 `user.human.added` events
- The webhook handler performs an UPSERT: INSERT on first arrival, UPDATE to enrich profile data if the user already exists via Create RPC
- The existing `Create` RPC and frontend provisioning flow remain unchanged (primary path)
- HMAC signature verification for webhook payload integrity
- Enable Zitadel Actions v2 feature flag and configure Target + Execution on the Zitadel instance

## Capabilities

### New Capabilities
- `zitadel-webhook-provisioning`: Webhook-based user provisioning from Zitadel Actions v2 events, providing profile enrichment as a complement to the existing RPC-based provisioning

### Modified Capabilities
- `user-account-sync`: Add webhook as a secondary provisioning path; UPSERT semantics to handle both Create RPC and webhook arriving in any order

## Impact

- **Backend**: New HTTP handler (outside Connect-RPC), HMAC signature verification middleware, UPSERT query in user repository
- **Protobuf/API**: No changes to existing RPC definitions
- **Database**: No schema changes (existing columns `preferred_language`, `name` will be populated by webhook)
- **Infrastructure**: Zitadel Actions v2 Target and Execution configuration (Zitadel Cloud admin)
- **Frontend**: No changes
