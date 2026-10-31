# Spec Delta

## ADDED Requirements

### Requirement: The invitation flow sets up no password

An invited person SHALL be able to set up a passkey as the only credential stored with their identity in the Organizer's Organization; signing in through an identity provider the Organization federates with stays available where the Organization has one. The hosted login SHALL offer no Password choice in the invitation flow or at first sign-in, and SHALL show its not-found page for any page that would set a password, also when that page's address is typed. The same hosted login serves fans, so the rules of the fan hosted login's "The hosted login offers no way to set a password" apply here unchanged.

#### Scenario: Invited person chooses a credential

- **WHEN** an invited person opens the invitation and the hosted login asks which credential to set up
- **THEN** Passkey is offered and Password is not, and after enrolling the passkey they arrive at the organizer console
- **AND** an identity provider the Organization federates with, if any, is still offered

#### Scenario: Set-password page opened by address

- **WHEN** an invited person opens the set-password page by typing its address
- **THEN** the hosted login shows its not-found page and no password is set
