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

#### Scenario: Return after a link sign-in

- **WHEN** an organizer on a new phone opens a console address, is shown the find-organizer screen and then signs in through the link in the email within 24 hours
- **THEN** the address they first opened is shown

## MODIFIED Requirements

### Requirement: Only owner-role operators enter, and they land on Home

The organizer console SHALL guard its screens: an unauthenticated visitor is sent to sign-in for the Organization the console knows (see "Without a known Organization the console asks for the email" for a console that knows none), and an authenticated user is admitted only if the token's `organizer-console` project roles include `owner`; otherwise the console shows a page saying access is denied, with a sign-out action. The backend remains the source of truth for authorization; the guard is a gate for the screens. An admitted operator SHALL land on the Home of their own Organizer, and an address the console does not know SHALL open that Home.

#### Scenario: Unauthenticated visitor goes to sign-in

- **WHEN** an unauthenticated visitor opens any console address on a device that remembers their Organizer's Organization, or with the Organization in the address
- **THEN** they are sent to sign-in for that Organization, and after signing in they return to the address they opened

#### Scenario: Owner lands on Home

- **WHEN** an authenticated operator whose token carries the `owner` role opens the console
- **THEN** the Home of the operator's Organizer is shown, at an address that names that Organizer

#### Scenario: Account without the owner role

- **WHEN** an authenticated user whose token lacks the `owner` role opens the console
- **THEN** the access denied page is shown with a sign-out action, and no console screen opens

#### Scenario: Old or unknown address

- **WHEN** an operator opens `lottery/status/abc`, `/concerts` or any other address the console does not know
- **THEN** the Home of the operator's Organizer is shown
