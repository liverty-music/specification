## MODIFIED Requirements

### Requirement: Payout account status and onboarding

While the Organizer has a payout account, the page SHALL show its status in words — 確認中 (being verified) for pending, 有効 (active) for active, or 要対応 (action needed) for restricted. While the Organizer has no payout account, the page SHALL show no status and SHALL NOT say that the payout account could not be loaded. While the Organizer has no payout account or it is not active, the page SHALL explain that fans can still buy tickets and only the payout waits, and SHALL say before the member leaves the console what the setup is: that payouts go through Stripe, the payment provider of Liverty Music; that on Stripe's page the member enters the business, its representative's identity and the bank account to be paid into; and that the console moves to Stripe's page and Stripe brings the member back to the console's Home when done. It SHALL then offer, marked as opening an external site, Stripe で登録する (set up on Stripe) when there is no payout account, or Stripe で登録を続ける (continue setup on Stripe) when the account is pending or restricted. Either action SHALL ask Liverty Music for a fresh onboarding page through PayoutAccountService.StartOnboarding, stay unavailable until the answer arrives, and then open Stripe's onboarding page in the same tab. When the onboarding page cannot be prepared, the page SHALL stay, show Stripe のページを開けませんでした。もう一度お試しください。 (Stripe's page could not be opened; try again) and keep the action available. When Stripe brings the member back, whether onboarding was finished or its page had expired, the console SHALL open Home, which reads the payout account again and keeps showing the 要対応 item, opening this page at the payout account, while the account is not active.

#### Scenario: No payout account yet

- **WHEN** the Organizer has no payout account
- **THEN** the page shows no status and no load failure, says sales are not blocked, explains what is entered on Stripe and that Stripe brings the member back to Home, and offers Stripe で登録する

#### Scenario: Onboarding not finished

- **WHEN** the payout account is pending
- **THEN** the page shows 確認中, says sales are not blocked, explains what is entered on Stripe and that Stripe brings the member back to Home, and offers Stripe で登録を続ける

#### Scenario: Member goes to Stripe

- **WHEN** the member selects Stripe で登録する or Stripe で登録を続ける
- **THEN** the action is unavailable while the onboarding page is prepared, and the same tab then opens Stripe's onboarding page

#### Scenario: Stripe's page cannot be prepared

- **WHEN** the member selects Stripe で登録を続ける and the onboarding page cannot be prepared
- **THEN** the page stays, shows Stripe のページを開けませんでした。もう一度お試しください。 and not the server's message, and the action is available again

#### Scenario: Back from onboarding

- **WHEN** the member finishes onboarding on Stripe's page and Stripe brings them back
- **THEN** the console opens Home, which reads the payout account again: no payout item when the account is now active, or the 要対応 item 入金口座の登録が終わっていません while it is still pending

#### Scenario: Onboarding page expired

- **WHEN** the member opens Stripe's onboarding page after it expired and Stripe brings them back
- **THEN** the console opens Home with the 要対応 item, and selecting it opens Settings at the payout account with Stripe で登録を続ける

#### Scenario: Active account

- **WHEN** the payout account is active
- **THEN** the page shows 有効 and no onboarding action
