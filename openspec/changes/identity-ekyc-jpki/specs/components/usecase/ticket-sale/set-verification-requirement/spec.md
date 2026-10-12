## ADDED Requirements

### Requirement: Only マイナンバーカード verification satisfies a requirement

While IdentityVerifications are created only with the method マイナンバーカード (My Number Card), SetVerificationRequirement SHALL let an Organizer choose Verified-any or JPKI-only, and both SHALL admit the same fans: those whose Active IdentityVerification was made with マイナンバーカード. No driver's licence fallback is offered, so a fan without a マイナンバーカード cannot take part in a sale that requires verification.

#### Scenario: Verified-any admits only マイナンバーカード verifications
- **WHEN** an Organizer sets Verified-any on a sale
- **THEN** only fans with an Active IdentityVerification made with マイナンバーカード can take part, as with JPKI-only

#### Scenario: Fan without a マイナンバーカード
- **WHEN** a sale requires verification and a fan has no マイナンバーカード
- **THEN** the fan cannot obtain an IdentityVerification and cannot take part in the sale
