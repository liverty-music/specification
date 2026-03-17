## Why

Signup 時に入力された email アドレスが検証されていない。Zitadel の Hosted Login は SMTP 設定があれば自動で OTP 検証を挟むが、現在 SMTP が未設定のためスキップされている。未検証メールのユーザーがシステムに入ると、通知の不達、なりすまし、データ品質低下のリスクがある。

SMTP 設定は cloud-provisioning (Postmark + Zitadel SmtpConfig) の別 change で対応する前提。この change では Frontend と Backend に `email_verified` の defense-in-depth チェックを追加し、SMTP 設定完了後に即座にシステム全体でメール検証が機能する状態にする。

## What Changes

- Zitadel Action (`add-email-claim.js`) を拡張し、access token に `email_verified` claim を注入する
- Backend の `Claims` struct に `EmailVerified` フィールドを追加し、`JWTValidator` で抽出する
- Backend の `ClaimsBridgeInterceptor` で `email_verified == false` の場合 `CodeUnauthenticated` を返す
- Frontend の `auth-callback.ts` で OIDC ID token の `email_verified` を確認し、未検証の場合はエラー表示する

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `authentication`: `email_verified` claim の検証要件を追加。Backend は access token の `email_verified` claim が `true` でないリクエストを拒否する。Frontend は callback 時に ID token の `email_verified` を確認する。

## Impact

- **cloud-provisioning**: `add-email-claim.js` に `email_verified` claim 追加（Zitadel Action）
- **backend**: `internal/infrastructure/auth/` — Claims struct, JWTValidator, ClaimsBridgeInterceptor の変更
- **frontend**: `src/routes/auth-callback.ts` — email_verified チェック追加、未検証時のエラーハンドリング
- **E2E テスト**: テスト用ユーザーは email_verified = true が前提。Zitadel Action が dev 環境で動作している必要あり
