## Why

The email address check uses two words for one action. The email and the email verification screen say 確認 (「メールアドレスの確認」, 「メールアドレスを確認する」, 「確認しました」). Settings then calls the result 認証 (「認証済み」 / 「未認証」).

That mix causes two problems:

- **Two words in one card.** The badge sits directly above the 本人確認 row, which already says 「確認済み」 / 「未確認」.
- **認証 means something else.** Elsewhere in the app, 認証 means signing in and card authentication (「認証情報」, 「カード認証」).

A fan who just tapped 「メールアドレスを確認する」 should see that same action reported as done.

## What Changes

- **Badge.** The Settings email verification badge reads 「確認済み」 when the address is verified and 「未確認」 when it is not. It currently reads 「認証済み」 / 「未認証」.
- **Error message.** The resend error in Settings says 「確認メール」 instead of 「認証メール」, the word the email itself uses.
- **English is unchanged.** It already uses one word throughout ("Verify email address", "Verified", "Not verified", "verification email").

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/settings`: the badge requirement names 「確認済み」, and now also names 「未確認」 for an address that is not verified.
- `stories/verify-email-address`: the walk-through scenario expects Settings to show 「確認済み」.

## Impact

- **frontend**: the ja strings `settings.emailVerified`, `settings.emailNotVerified` and `settings.resendError`, plus a fixture test that reads the badge label in both states. No code or layout change.
- **backend, cloud-provisioning, proto**: none. The verification email and the `/verify-email` screen already say 確認.
