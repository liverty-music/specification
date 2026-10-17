# Spec Delta

## ADDED Requirements

### Requirement: SendSignInLinks needs no sign-in and reveals nothing

SendSignInLinks SHALL be callable without a sign-in. It SHALL take an email address, fail with InvalidArgument when it is missing or not an email address, and run OrganizerUseCase.SendSignInLinks with it, identifying the client for the per-client limit by its network address. It SHALL answer with an empty success whenever the usecase succeeds, whether or not any Organizer has the address, and SHALL return ResourceExhausted unchanged. It is the only call of the organizer Organizer service that needs no sign-in.

#### Scenario: Owner asks for sign-in links

- **WHEN** SendSignInLinks is called without a sign-in for the owner email of an active Organizer
- **THEN** it succeeds with an empty response and the owner receives the links

#### Scenario: Unknown address

- **WHEN** SendSignInLinks is called for an address that owns no Organizer
- **THEN** it succeeds with the same empty response

#### Scenario: Malformed address

- **WHEN** SendSignInLinks is called with `band@`
- **THEN** it fails with InvalidArgument

#### Scenario: Too many requests

- **WHEN** the client exceeded the per-client limit
- **THEN** it fails with ResourceExhausted
