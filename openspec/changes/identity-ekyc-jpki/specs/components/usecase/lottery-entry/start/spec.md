## ADDED Requirements

### Requirement: Verification adds no verified name

When the sale requires verification, Start SHALL use the fan's IdentityVerification only for the verification gate and SHALL NOT read a name from it or compare it with the User's full name. The entry's 本人確認 (identity check) details stay the User's self-declared full name and phone number; the IdentityVerification contributes the provider user ID that identifies the person, not a verified name.

#### Scenario: Verified fan starts an entry
- **WHEN** a fan with an Active IdentityVerification starts an entry for a TicketType of a sale that requires JPKI-only
- **THEN** Start returns the Draft without reading a name from the IdentityVerification, and the entry's 本人確認 details are the User's full name and phone number
