# Spec Delta

## ADDED Requirements

### Requirement: The identity verification result is shown on Settings

When a fan returns from the PocketSign app, the verification callback address SHALL show only a progress indicator while the result is confirmed, and SHALL then open Settings without keeping the callback address in the history. On success, Settings SHALL show the snackbar "本人確認が完了しました" and the identity verification badge SHALL read 確認済み without a reload. On failure, Settings SHALL show the reason inside the identity verification row, next to the 本人確認する button, and SHALL keep it until the fan starts verification again. The reasons are: no verification in progress on this device; verification not available right now; the card read did not finish or has expired; the verification details did not match; something else went wrong. When the card was already used to verify another account, Settings SHALL NOT offer 本人確認する and SHALL show the reason with the support contact. When this device has no verification in progress and the fan already has an Active IdentityVerification, Settings SHALL show no failure.

#### Scenario: Verification succeeds

- **WHEN** a fan returns from the PocketSign app and the verification is confirmed
- **THEN** Settings opens, shows the snackbar "本人確認が完了しました", the identity verification badge reads 確認済み and 本人確認する is not shown

#### Scenario: Card read not finished

- **WHEN** a fan returns from the PocketSign app before the card read finished
- **THEN** Settings opens with "カードの読み取りが終わっていないか、期限が切れました。もう一度お試しください。" next to 本人確認する, and the reason is still shown 10 seconds later

#### Scenario: Card already used by another account

- **WHEN** the card was already used to verify another account
- **THEN** Settings shows that reason with the support contact and does not show 本人確認する

#### Scenario: Verification unavailable

- **WHEN** verification is not available when the fan returns
- **THEN** Settings shows "本人確認は現在ご利用いただけません。時間をおいてお試しください。" next to 本人確認する

#### Scenario: Callback opened again after success

- **WHEN** the callback address is opened again after the fan was verified
- **THEN** Settings opens with the identity verification badge 確認済み and no failure reason

#### Scenario: No verification on this device

- **WHEN** the callback address is opened on a device with no verification in progress and the account is unverified
- **THEN** Settings shows "本人確認の手続きが見つかりませんでした。設定画面からもう一度お試しください。" next to 本人確認する

#### Scenario: Retry clears the reason

- **WHEN** a failure reason is shown and the fan presses 本人確認する
- **THEN** the reason is no longer shown
