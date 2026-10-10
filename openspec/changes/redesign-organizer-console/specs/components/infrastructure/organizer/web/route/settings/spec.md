# Spec Delta

## Purpose

The organizer console page that shows who the Organizer is to Liverty Music and to fans: its name, the Artists it represents, its business details shown on ticket sales, and the state of its payout account.

## ADDED Requirements

### Requirement: Organization and represented Artists

The page SHALL show the Organizer's name and the Artists it represents, read only, and SHALL say that Liverty Music changes them on request.

#### Scenario: Two represented Artists

- **WHEN** the Organizer XX Records represents Band A and Band B
- **THEN** the page shows XX Records with Band A and Band B

### Requirement: Business details, read only

The page SHALL show the Organizer's business details — legal name, representative name, business address, business phone number and contact email — read only, and SHALL say that Liverty Music entered them during vetting, that they are shown to fans on ticket sales as the seller disclosure (特商法 表記, the commercial transactions disclosure), and how to ask Liverty Music to change them. A missing detail SHALL be shown as 未登録 (not registered), with a note that sales cannot start until every detail is registered.

#### Scenario: Complete details

- **WHEN** all five business details are registered
- **THEN** the page shows them and no warning

#### Scenario: Address missing

- **WHEN** the business address is not registered
- **THEN** the address shows 未登録 and the page says sales cannot start until it is registered

### Requirement: Payout account status and onboarding

The page SHALL show the payout account's status in words — 確認中 (being verified) for pending, 有効 (active) for active, or 要対応 (action needed) for restricted — and, while the account is not active, SHALL explain that fans can still buy tickets and only the payout waits, and offer 登録を続ける (continue setup), which opens the provider's onboarding page in a new tab. When the operator returns to the console tab, the page SHALL read the status again.

#### Scenario: Onboarding not finished

- **WHEN** the payout account is pending
- **THEN** the page shows 確認中, says sales are not blocked, and offers 登録を続ける

#### Scenario: Back from onboarding

- **WHEN** the operator finishes onboarding in the other tab and returns to the console tab
- **THEN** the page reads the status again and shows the new status

#### Scenario: Active account

- **WHEN** the payout account is active
- **THEN** the page shows 有効 and no onboarding action
