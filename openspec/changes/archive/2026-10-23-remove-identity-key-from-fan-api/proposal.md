## Why

The fan API pod mounts the `backend-app` identity-provider key, whose `ORG_USER_MANAGER` membership can change or delete every fan identity (`user.write`, `user.delete`). A compromise of the internet-facing fan API therefore hands over every fan account: the attacker can rewrite an email and recover the account through it. The only fan-facing call that needs the key is ResendEmailVerification. Account deletion (`UserUseCase.Delete`) is admin-only and is served by the admin console API, which keeps its own copy of the key. The organizer console API and the reception API mount the same key and also read it from the shared `backend-secrets`, though nothing they route uses it: the binary builds the clients at startup whether or not they are called. Least privilege (RFC 9700 §2.3; OWASP ASVS 5.0 8.3.3) says the internet-facing tier should hold no standing credential over all users when it does not need one.

## What Changes

- ResendEmailVerification only counts the request against the caller's limit and announces a resend request. The event consumer, which already sends the first verification email with the same key, sends the fresh code.
- The fan API answers a resend request for an address that is already verified with success instead of FailedPrecondition. The event consumer then sends nothing. The Settings button is shown only while the address is unverified, so the screen behaves as before. The Unavailable answer for "email verification not configured" moves out of the fan API with the key.
- The fan, organizer console and reception API deployments no longer mount or read the `backend-app` key. It moves out of the shared `backend-secrets` into the dedicated Secrets of the admin console API and the event consumer.
- The backend requires the key only on the admin workload (and the event consumer), not on every API workload.
- A new rule for backend processes records that only the admin console API and the event consumer hold an identity-provider credential.

## Capabilities

### New Capabilities

- `components/usecase/user/reissue-email-verification`: UserUseCase.ReissueEmailVerification - run for each announced resend request and send the fresh verification code.
- `components/infrastructure/backend/process/identity-provider-credentials`: the fan, organizer and reception API servers hold no credential for the identity provider's management API; only the admin console API and the event consumer do.

### Modified Capabilities

- `components/usecase/user/resend-email-verification`: it announces instead of sending. An already-verified address and a missing configuration are no longer errors seen by the caller.

- `components/adapter/fan/api/rpc/user`: ResendEmailVerification succeeds once the usecase has announced the request; the code is sent later by the event consumer.

User.ResendVerification and User.Get are relied on unchanged.

## Impact

- **backend**: the resend usecase publishes `USER.email_verification_resend_requested` (`{user_id}`), and a new consumer handler sends the code. The server config requires the key only on the admin workload; DI on the other workloads runs without it.
- **cloud-provisioning**, in two PRs:
  - Before the backend: a NACK Consumer and a KEDA trigger for the new consumer.
  - After the backend: remove the key from `fan-api`, `organizer-console-api` and `reception-api`, and move it from `backend-secrets` into `event-consumer-secrets` and `admin-console-api-secrets`.
- **frontend**: none.
- **Related**: `fan-passkey-recovery-and-management` already keeps its new identity-provider key off the fan API. Together the two changes leave the fan, organizer and reception APIs with no identity-provider credential.
