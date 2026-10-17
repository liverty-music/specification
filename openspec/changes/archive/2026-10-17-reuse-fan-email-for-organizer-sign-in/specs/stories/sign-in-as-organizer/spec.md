# Spec Delta

## ADDED Requirements

### Requirement: One email serves the fan account and the Organizer

A person SHALL be able to run an Organizer with the email of their fan account. The admin creates the Organizer with that email and a short name (OrganizerUseCase.Create), the person accepts the invitation and registers a passkey for their identity in the Organizer's Organization, and afterwards the fan app signs them in to the fan account and the organizer console to the Organizer, each after they type the same email and each with its own passkey. No user name is ever typed. Neither account can be reached through the other.

#### Scenario: Fan becomes an Organizer's owner

- **WHEN** an admin creates the Organizer `xx-records` with the email of an existing fan account, and the person accepts the invitation
- **THEN** the Organizer is active, the person signs in to the console by typing that email and using the new passkey, the sign-in shows `<email> (xx-records)`, and the fan app still signs them in to the fan account with the old passkey

### Requirement: A new device finds the Organizer by short name or by email

An organizer who opens the console on a device that remembers no Organization SHALL reach their Organizer's sign-in either through `https://organizer.liverty-music.app/?org=<short name>` or, from the find-organizer screen, through an emailed sign-in link for each Organizer they own (OrganizerUseCase.SendSignInLinks), and SHALL sign in to the right Organizer's Organization, never to their fan account.

#### Scenario: Owner on a new phone with the short name

- **WHEN** the owner of `xx-records`, who also has a fan account with the same email, opens `https://organizer.liverty-music.app/?org=xx-records` on a new phone and types the email
- **THEN** they sign in to xx-records' Organization and land on its Home

#### Scenario: Owner on a new phone without the short name

- **WHEN** the same owner opens the console without `?org`, enters the email on the find-organizer screen and opens the link from the email
- **THEN** they sign in to xx-records' Organization and land on its Home
