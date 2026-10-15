# Spec Delta

## ADDED Requirements

### Requirement: Without a known Organization the console asks for the email

When an unauthenticated visitor opens any console address and the console knows no Organization - none in the address and none remembered on the device - the console SHALL open the find-organizer screen instead of starting a sign-in, and SHALL return the visitor to the address they opened once they sign in through a link. When the console knows an Organization, the guard sends the visitor to sign-in for that Organization as before.

#### Scenario: New device

- **WHEN** an organizer opens `https://organizer.liverty-music.app/` on a new phone
- **THEN** the find-organizer screen is shown and no sign-in starts

#### Scenario: Remembered Organization

- **WHEN** the organizer opens the console on a device where they signed in before
- **THEN** the sign-in for their Organizer's Organization starts
