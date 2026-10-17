# components/infrastructure/organizer/web/route/find-organizer Specification

## Purpose
The organizer console's screen for a device that does not know which Organizer the visitor runs: it asks for the email and sends the sign-in links for that person's Organizers, without saying whether the email runs any.

## Requirements

### Requirement: The screen asks for the email and always answers the same way

The find-organizer screen SHALL ask for the email the visitor uses for their Organizer, with a send action, and SHALL check that the input is an email address before sending, showing the problem next to the field. After OrganizerService.SendSignInLinks succeeds it SHALL say, in the console's language, that when the address runs an Organizer on Liverty Music an email with a sign-in link has been sent, that the link opens the console for that Organizer, and that a person who runs no Organizer should contact Liverty Music; this message SHALL be the same for every address. When the call fails with ResourceExhausted it SHALL say to try again later. The screen SHALL not show any Organizer, Organization or sign-in form.

#### Scenario: Owner asks for the link

- **WHEN** an owner enters their email and sends
- **THEN** the screen says a sign-in link has been sent if the address runs an Organizer, and the owner receives the email

#### Scenario: Address that runs nothing

- **WHEN** a visitor enters an address that runs no Organizer and sends
- **THEN** the screen shows exactly the same message as for an owner

#### Scenario: Malformed address

- **WHEN** a visitor enters `band@` and sends
- **THEN** the screen says the email address is not valid, next to the field, and nothing is sent

#### Scenario: Too many requests

- **WHEN** SendSignInLinks fails with ResourceExhausted
- **THEN** the screen says to try again later

### Requirement: A sign-in link opens the console for its Organizer

A sign-in link from the email SHALL open the organizer console tied to that Organizer's Organization, start the sign-in for it, and remember the Organization on the device for later sign-ins.

#### Scenario: Link opened

- **WHEN** the owner opens the sign-in link for XX Records
- **THEN** the sign-in for XX Records' Organization starts, and after signing in with their passkey they land on XX Records' Home; the next visit on that device starts the same sign-in without the link
