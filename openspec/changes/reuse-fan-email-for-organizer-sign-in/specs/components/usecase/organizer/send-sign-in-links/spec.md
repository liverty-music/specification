# Spec Delta

## Purpose

OrganizerUseCase.SendSignInLinks lets a person who opens the organizer console on a device that does not know their Organizer receive, by email, a sign-in link for each Organizer they own, without anyone learning from the answer whether an address owns an Organizer.

## ADDED Requirements

### Requirement: The owner's Organizers are sent to the owner's mailbox only

SendSignInLinks SHALL take an email address and read the Organizers it owns through Organizer.ListByOwnerEmail. When the list is not empty, it SHALL send their sign-in links through Organizer.SendSignInLinks. When the list is empty, it SHALL send nothing. In both cases it SHALL succeed in the same way, so the caller cannot tell whether the address owns an Organizer. A failure to read or to send SHALL be logged and SHALL NOT fail the call.

#### Scenario: Owner asks for links

- **WHEN** SendSignInLinks runs for the owner email of an active Organizer
- **THEN** the email with that Organizer's sign-in link is sent and the call succeeds

#### Scenario: Address that owns nothing

- **WHEN** SendSignInLinks runs for an address that owns no active Organizer
- **THEN** no email is sent and the call succeeds exactly as for an owner

#### Scenario: Mail service unavailable

- **WHEN** Organizer.SendSignInLinks fails with Internal
- **THEN** the call still succeeds and the failure is logged

### Requirement: Requests per address and per client are limited

SendSignInLinks SHALL send at most 3 emails per address in any 60 minutes; a further request for that address within the window SHALL succeed without sending. Requests from one client SHALL be limited to 10 in any 60 minutes; a further request SHALL fail with ResourceExhausted.

#### Scenario: Fourth request for one address

- **WHEN** links were sent to an address 3 times in the last 60 minutes and a fourth request for it arrives
- **THEN** the call succeeds and no email is sent

#### Scenario: Eleventh request from one client

- **WHEN** one client made 10 requests in the last 60 minutes and makes another
- **THEN** it fails with ResourceExhausted
