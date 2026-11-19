# Spec Delta

## MODIFIED Requirements

### Requirement: Sign-in help link next to Log In

Wherever the welcome page shows the `[Log In]` CTA, it SHALL show a "can't sign in" text link directly below it that opens the sign-in help screen. The link SHALL be a native link with a minimum tap target of 48px height.

#### Scenario: Link below Log In

- **WHEN** an unauthenticated user sees the `[Log In]` CTA on Screen 2 or in the Screen 1 fallback
- **THEN** a "can't sign in" link is shown directly below it

#### Scenario: Link opens the sign-in help screen

- **WHEN** the user taps the "can't sign in" link
- **THEN** the app navigates to `/sign-in-help`

## ADDED Requirements

### Requirement: The screen's address

The welcome page SHALL be served at `/welcome`, and `/` SHALL lead to it.

#### Scenario: The page's address
- **WHEN** a guest opens `/`
- **THEN** the app shows the welcome page at `/welcome`
