## Why

Users who sign up via the Passkey flow currently have their email auto-verified by a Zitadel Action (`autoVerifyEmail`), meaning they never actually confirm ownership of their email address. Email verification is required for future ticket sales and builds user trust. Testing confirmed that removing the auto-verify Action does NOT block the Passkey OIDC flow — users can sign up and log in without email verification. However, Zitadel does not automatically send verification emails for Passkey registrations, so the backend must explicitly trigger verification via the Zitadel API.

## What Changes

- **Remove** the `autoVerifyEmail` Zitadel Action and its trigger (cloud-provisioning)
- **Add** a Zitadel Machine User (service account) with Private Key JWT credentials for backend-to-Zitadel API communication (cloud-provisioning)
- **Add** `zitadel-go/v3` SDK integration in backend to call Zitadel Admin APIs
- **Add** a `USER.created` NATS/JetStream event published on user provisioning (backend)
- **Add** a consumer that listens to `USER.created` and triggers email verification via `POST /v2/users/{userId}/email/send` (backend)
- **Add** a resend verification email RPC endpoint in backend, proxying to Zitadel's `POST /v2/users/{userId}/email/resend`
- **Add** email verification status display and resend button on the Settings page (frontend)
- **Update** the `identity-management` spec to replace auto-verify with the new verification flow

## Capabilities

### New Capabilities

- `email-verification`: Covers the end-to-end email verification flow — triggering verification on user creation, resending verification emails, and displaying verification status in the UI.
- `zitadel-service-account`: Covers the Zitadel Machine User provisioning, Private Key JWT credential management, and GCP Secret Manager integration for backend-to-Zitadel API authentication.

### Modified Capabilities

- `identity-management`: The "Auto-Verify Email on Self-Registration" requirement is removed. Users are now created with unverified email, and verification happens asynchronously via backend.
- `email-provider`: No requirement changes — SMTP configuration remains the same. The email-provider capability already covers Postmark SMTP delivery, which this change relies on.

## Impact

- **cloud-provisioning**: Remove `autoVerifyEmail` Action/Trigger, add Machine User + key + IAM role, store key in Secret Manager
- **backend**: New dependency on `zitadel-go/v3`, new NATS stream (`USER`), new consumer, new RPC endpoint for resend, new configuration for Zitadel API client
- **frontend**: Settings page UI changes (verification status + resend button)
- **Zitadel**: `addEmailClaim` Action's `email_verified` claim will now reflect real verification state instead of always being `true`
- **Proto**: New RPC method for resending verification email (in UserService or new service)
