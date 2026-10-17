# Spec Delta

## ADDED Requirements

### Requirement: A fan signs in with their email as before

The product organization SHALL keep its identities' sign-in names equal to their emails, unique across the identity provider's product and admin organizations, so a fan keeps signing in by typing their email and their passkey shows that email, whatever an Organizer's Organization does with the same email.

#### Scenario: Fan whose email also runs an Organizer

- **WHEN** a fan whose email is also the owner email of an Organizer signs in to the fan app with that email
- **THEN** they sign in to their fan account with its passkey, and the sign-in name shown is their email
