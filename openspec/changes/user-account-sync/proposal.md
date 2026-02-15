## Why

Users who sign up via Zitadel are only registered in the identity provider's database. The liverty-music backend database has no record of these users, which means user-specific features (artist following, personalized notifications) cannot associate data with authenticated users. An account synchronization mechanism is needed to bridge the gap between Zitadel and the application database.

## What Changes

- Add `external_id` (UUID) column to the `users` table to store the Zitadel `sub` claim, enabling identity-to-application mapping
- Add `external_id` field to the `User` protobuf entity; `Create` RPC accepts `email` parameter (external_id extracted from JWT)
- Extend the frontend registration callback to call the backend `Create` RPC immediately after signup, using OIDC `state` to detect registration vs login
- Update the User entity, repository, and protobuf definitions to support `external_id`-based lookup
- Document the sync architecture decision (MVP: client-side provisioning; future: Zitadel Actions v2 Webhook)

## Capabilities

### New Capabilities

- `user-account-sync`: Synchronizes user accounts from Zitadel to the application database on first registration

### Modified Capabilities

- `user-auth`: Add post-signup account provisioning step to the login callback flow
- `authentication`: Add `external_id` (Zitadel `sub`) as the primary identity lookup key alongside internal user ID

## Impact

- **Database**: New migration adding `external_id` column with unique constraint to `users` table
- **Protobuf**: `User` entity gains `external_id` field; `Create` RPC accepts `email` (breaking change - field 1 type changed)
- **Backend**: User repository, use case, and RPC handler updated for `external_id` support; handler extracts `sub` from JWT
- **Frontend**: `auth-service.ts` passes `state` on registration; `auth-callback.ts` calls `Create` RPC on signup
- **Breaking changes**: `CreateRequest` message field 1 changed from `User user` to `UserEmail email`
