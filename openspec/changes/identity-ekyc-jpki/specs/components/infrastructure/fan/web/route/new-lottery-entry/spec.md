# Spec Delta

## ADDED Requirements

### Requirement: An unverified fan is asked to verify before entering

When the sale requires verification, the entry screen SHALL read the fan's IdentityVerification with IdentityVerificationService.Get when it opens. When the fan has no IdentityVerification or it is not Active, the screen SHALL say that the sale requires マイナンバーカード verification and SHALL offer the way to verify on Settings instead of the ticket count, so no card is authorized. When the IdentityVerification cannot be read for another reason, the screen SHALL let the fan continue; LotteryEntryService.AuthorizeCard checks the requirement again.

#### Scenario: Unverified fan on a sale that requires verification
- **WHEN** a fan who never verified opens the entry screen for a TicketStock of a sale that requires JPKI-only
- **THEN** the screen says the sale requires マイナンバーカード verification and offers to verify on Settings, and no card is authorized

#### Scenario: Verified fan on a sale that requires verification
- **WHEN** a fan with an Active IdentityVerification opens the same entry screen
- **THEN** the screen offers the ticket count as usual

#### Scenario: Verification cannot be read
- **WHEN** reading the fan's IdentityVerification fails with Unavailable
- **THEN** the screen offers the ticket count, and an unverified fan is stopped by LotteryEntryService.AuthorizeCard with FailedPrecondition
