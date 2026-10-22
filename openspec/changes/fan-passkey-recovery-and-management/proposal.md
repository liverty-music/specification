## Why

The fan app asks every fan to sign up with a passkey, but a fan can only ever use the passkey they created at sign-up. The app has no way to add a passkey on another device, to see or remove passkeys, or to get back in after losing the device: password reset is hidden and the fan specs, unlike the organizer specs, require no recovery path. A fan whose passkey is not synced (or who moves between ecosystems, e.g. iPhone to Windows) is locked out for good.

Every primary source checked agrees on the baseline this change adopts: allow several passkeys per account and manage them in account settings (FIDO Alliance design guidelines, required patterns; web.dev "passkey management"), keep a recovery path for passkey-only accounts (Google passkey user journeys; NIST SP 800-63B-4 §4.1.2.1 "SHALL permit the binding of multiple authenticators", §4.2 recovery), and notify the fan when an authenticator is added (NIST §4.1.2.1 SHALL).

## What Changes

- **Recovery by email**: a fan who cannot sign in enters their email on a new "can't sign in" screen reachable from the welcome page and the Settings guest hero. When the address belongs to a fan account with a verified address, the fan receives a link (valid 1 hour) that registers a new passkey on the device they open it on. The answer and its timing never reveal whether an account exists; requests are limited per address and per client.
- **Passkey management in Settings**: a signed-in fan sees their passkeys (name), adds a passkey on the device in hand, and removes passkeys they no longer use. Opening passkey management requires a sign-in within the last 5 minutes. The last remaining passkey cannot be removed from the app.
- **Security notifications**: the fan receives an email whenever a passkey is added to or removed from their account, including a passkey added through a recovery link.
- **Hosted login policy described as it is**: the fan hosted-login spec currently requires local authentication to be off ("passkeys-only"), which the identity provider cannot honor because that switch also disables passkeys; the spec is corrected to express passkey-only as "passwordless allowed and no password ever issued", like the organizer spec, and gains the recovery-path requirement.
- New public fan RPC `UserService.RequestPasskeyRecovery(email)`.

## Capabilities

### New Capabilities

- `components/entity/user/get-by-email`: read the User whose email matches an address, ignoring letter case; NotFound otherwise.
- `components/entity/user/send-passkey-registration-link`: send the User's verified address a single-use link, valid 1 hour, that registers a new passkey for the User.
- `components/entity/user/send-passkey-change-email`: email the User that a passkey was added to or removed from their account.
- `components/usecase/user/request-passkey-recovery`: UserUseCase.RequestPasskeyRecovery - accept an email, limit requests, and announce a recovery request for the matching User without revealing whether one exists.
- `components/usecase/user/send-passkey-recovery-link`: UserUseCase.SendPasskeyRecoveryLink - run for each announced recovery request and send the registration link.
- `components/usecase/user/notify-passkey-change`: UserUseCase.NotifyPasskeyChange - run for each passkey added or removed at the identity provider and email the fan.
- `components/adapter/fan/api/webhook/passkey-events`: the identity provider's passkey-added and passkey-removed notices, authenticated and turned into announcements.
- `components/infrastructure/fan/web/route/passkey-recovery`: the "can't sign in" screen.
- `stories/recover-sign-in-after-losing-passkeys`: a fan who lost every passkey gets back into the same account.
- `stories/manage-passkeys`: a fan adds a passkey on another device, sees and removes passkeys, and is told about each change.

### Modified Capabilities

- `components/adapter/fan/api/rpc/user`: RequestPasskeyRecovery is the one user service call that needs no sign-in; new requirement for its handling.
- `components/infrastructure/fan/web/route/settings`: new Passkeys section for signed-in fans; the guest hero gains the "can't sign in" link.
- `components/infrastructure/fan/web/route/welcome`: the sign-in CTAs gain the "can't sign in" link.
- `components/infrastructure/fan/web/global/hosted-login`: "Configure Login Policy" corrected to the policy the product actually runs; new requirements for the recovery path and for registering a passkey from a link or from a signed-in session.

The User entity (Purpose) is unchanged: no attribute is added (passkeys live at the identity provider and are not stored by the platform). The usecases also rely on the existing operations User.Get and User.GetByProviderUserID, whose promises are unchanged.

## Impact

- **specification**: `rpc/user/v1/user_service.proto` gains `RequestPasskeyRecovery`; a Release and BSR generation are needed before backend and frontend PRs.
- **backend**: new usecase methods, a public RPC with per-address and per-client limits, two new event subjects and consumer handlers, a webhook handler for passkey events, a Postmark email for passkey changes, and an identity-provider client that issues passkey registration links.
- **frontend**: "can't sign in" screen, links from welcome and the Settings guest hero, a Passkeys section in Settings that talks to the identity provider directly with a short-lived, re-authenticated token.
- **cloud-provisioning**: a dedicated identity-provider service account for recovery links (mounted on the event consumer only), Actions v2 targets and event executions for passkey events, the login policy left as is, and review of the identity provider's passkey-registration email text.
- **Out of scope**: the ticket wallet key stays one device per User; removing the identity-provider key from the fan API (account deletion and verification resend) is a separate change.
