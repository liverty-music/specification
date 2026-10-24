## 1. Settings wording (frontend)

- [x] 1.1 Change the ja strings `settings.emailVerified` to 「確認済み」, `settings.emailNotVerified` to 「未確認」 and `settings.resendError` to say 「確認メール」 (en unchanged). Verify a fixture test of the Settings account row reading the badge label for components/infrastructure/fan/web/route/settings "Verified on another device" (確認済み, no resend action) and "Not yet verified" (未確認 beside 再送信), and `make check`
- [x] 1.2 Merge and release; confirm `fan-web-app` rolled out in prod, then open Settings in Japanese on the deployed app with the owner account (Playwright or a browser) and see 確認済み on the email row

@spec-manual stories/verify-email-address "Sign up, then verify on the phone" -- verified end to end in fan-email-verification-in-app task 6.1 (2026-10-24); this change only renames the badge, checked on the deployed app in task 1.2
