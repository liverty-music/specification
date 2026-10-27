## ADDED Requirements

### Requirement: Verification adds no verified name

When the sale requires verification, AuthorizeCard SHALL use the fan's IdentityVerification only for the verification gate and SHALL NOT read a name from it or compare it with the User's full name. The 本人確認 (identity check) details of the entry stay the User's self-declared full name and phone number; the IdentityVerification contributes the provider user ID that identifies the person, not a verified name.

#### Scenario: Verified fan authorizes their card
- **WHEN** a fan with an Active IdentityVerification authorizes their card for a TicketType of a sale that requires JPKI-only
- **THEN** AuthorizeCard opens the card authorization without reading a name from the IdentityVerification, and the 本人確認 details are the User's full name and phone number
