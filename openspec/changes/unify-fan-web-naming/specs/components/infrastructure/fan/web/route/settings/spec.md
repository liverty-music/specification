# Spec Delta

## MODIFIED Requirements

### Requirement: Guest hero offers sign-in help

The guest call-to-action hero at the top of the Settings page SHALL show a "can't sign in" text link below its sign-in and sign-up actions that opens the sign-in help screen.

#### Scenario: Guest opens sign-in help from Settings

- **WHEN** an unauthenticated user taps "can't sign in" in the Settings guest hero
- **THEN** the app navigates to `/sign-in-help`

## ADDED Requirements

### Requirement: The screen's address

Settings SHALL be served at `/settings`.

#### Scenario: The screen's address
- **WHEN** a fan opens Settings
- **THEN** the address bar shows `/settings`
