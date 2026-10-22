## Why

The fan API pod mounts the `backend-app` identity-provider key, whose `ORG_USER_MANAGER` membership can change or delete every fan identity (`user.write`, `user.delete`). A compromise of the internet-facing fan API therefore hands over every fan account: the attacker can rewrite an email and recover the account through it. The only fan-facing call that needs the key is ResendEmailVerification. Account deletion (`UserUseCase.Delete`) is admin-only and is served by the admin console API, which keeps its own copy of the key. Least privilege (RFC 9700 §2.3; OWASP ASVS 5.0 8.3.3) says the internet-facing tier should hold no standing credential over all users when it does not need one.

## What Changes

- ResendEmailVerification only counts the request against the caller's limit and announces a resend request. The event consumer, which already sends the first verification email with the same key, sends the fresh code.
- The fan API answers a resend request for an address that is already verified with success instead of FailedPrecondition. The event consumer then sends nothing. The Settings button is shown only while the address is unverified, so the screen behaves as before. The Unavailable answer for "email verification not configured" moves out of the fan API with the key.
- The fan API deployment no longer mounts the `backend-app` key. The admin console API and the event consumer keep it.
- A new server-wide rule records that the fan API holds no identity-provider credential.

## Capabilities

### New Capabilities

- `components/usecase/user/reissue-email-verification`: UserUseCase.ReissueEmailVerification - run for each announced resend request and send the fresh verification code.
- `components/infrastructure/fan/api/server/identity-provider-credentials`: the fan API server holds no credential for the identity provider's management API.

### Modified Capabilities

- `components/usecase/user/resend-email-verification`: it announces instead of sending. An already-verified address and a missing configuration are no longer errors seen by the caller.

User.ResendVerification and User.Get are relied on unchanged.

## Impact

- **backend**: the resend usecase publishes `USER.email_verification_resend_requested` (`{user_id}`), and a new consumer handler sends the code. DI on the fan API runs without the key.
- **cloud-provisioning**: remove the key volume and mount from the `fan-api` deployment and its ExternalSecret entry, and add a KEDA trigger for the new consumer.
- **frontend**: none.
- **Related**: `fan-passkey-recovery-and-management` already keeps its new identity-provider key off the fan API. Together the two changes leave the fan API with no identity-provider credential.
