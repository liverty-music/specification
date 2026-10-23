## Why

Passkey recovery sends its link only to a verified address, so email verification now decides whether a fan can get back into their account. Verification works poorly today (#1228, found in the prod check on 2026-10-22/23):

- **The link ends on a page with no way back.** It opens the identity provider's page, which ends on "User verified" with no way back to the app.
- **The email is in the wrong language and voice.** It comes in the identity provider's language rather than the fan's (English for the owner's Japanese account). It is headed "Zitadel", and it says "a new email has been added" right after sign-up.
- **Settings shows a stale state.** A browser that signed in before verifying keeps showing 未認証 after a reload.

## What Changes

- **Our own verification email**:
  - The sign-up email and the Settings resend are sent by the platform, in the fan's preferred language, under the Liverty Music name.
  - It says the link works for 1 hour and to ignore it if the fan did not sign up.
  - The link opens the app's new **email verification screen**.
- **Verification from the app**: the screen needs no sign-in. It confirms the address only when the fan taps "メールアドレスを確認する", never on opening, so link scanners cannot use the code up. It then shows the result:
  - verified, with a way into the app;
  - the link expired or was already used, with how to get a new one.
- **New public fan RPC** `UserService.VerifyEmail(user, code)`: limited per client and per User, and answering the same way whether the User or the code is wrong.
- **Fresh verification state in Settings**: the badge reflects the identity provider's current state when Settings opens and when the fan comes back to the tab.
- **Depends on `identity-service`**: the fan API asks the identity service to verify, on a listener of its own that allows only that operation.

## Capabilities

### New Capabilities

- `components/entity/user/verify-email`: confirm a User's address with the code from the verification email; it fails when the code is wrong, expired or used.
- `components/usecase/user/verify-email`: UserUseCase.VerifyEmail lets anyone holding the link confirm that User's address, with limits per client and per User, and without revealing whether a User exists.
- `components/infrastructure/fan/web/route/verify-email`: the email verification screen.
- `stories/verify-email-address`: a fan who just signed up verifies their address from the email and returns to the app.

### Modified Capabilities

- `components/entity/user/send-verification`: the email is in the User's preferred language and links to the email verification screen.
- `components/entity/user/resend-verification`: the same as send-verification, for the fresh code.
- `components/adapter/fan/api/rpc/user`: VerifyEmail joins RequestPasskeyRecovery as a call that needs no sign-in, with its own handling requirement.
- `components/infrastructure/fan/web/route/settings`: the verification badge reflects the current state on opening and on returning to the tab.

`components/infrastructure/backend/process/identity-provider-credentials` changes too: the fan API reaches the identity service's verify operation and nothing else. That requirement is being rewritten by `identity-service`, so this change adds its delta after `identity-service` is archived (tasks).

Unchanged and relied on:
- `UserUseCase.ReissueEmailVerification`, `UserUseCase.ResendEmailVerification` (3 per 10 minutes per User) and the Create usecase's "verification email follows every new user";
- the entity operations `User.Get` and `User.SendVerification`'s callers.

## Impact

- **specification**: `rpc/user/v1/user_service.proto` gains `VerifyEmail`; `rpc/backend/user/v1` gains `VerifyEmail` (both on top of `identity-service`). Release and BSR generation.
- **backend**:
  - The consumer sends the verification email through Postmark (ja/en) with a code the identity service returns.
  - The fan API gains the public `VerifyEmail` with limiters and an identity-service client.
  - The identity service gains a fan-API listener allowing only `VerifyEmail`.
- **frontend**:
  - the `/verify-email` route;
  - the Settings badge refreshed from the identity provider's userinfo.
- **cloud-provisioning**:
  - the identity Service and NetworkPolicy gain the fan-API port;
  - `IDENTITY_SERVICE_URL` on `fan-api`.
- **Out of scope**:
  - prompting unverified fans to verify, which is not needed while there are no users;
  - the language of identity-provider pages opened from an email, which follows the browser, as expected.
