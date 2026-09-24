# OrganizerConnectedAccount.CreateOnboardingLink

## Purpose

Creates a link to the payment provider's hosted page where the Organizer starts or continues the identity check for its account.

## Requirements

### Requirement: CreateOnboardingLink returns a fresh single-use link

CreateOnboardingLink SHALL return a new link to the provider's hosted identity-check page for the account. The link SHALL be usable once and only for a short time, so it is never reused; when the Organizer finishes, or opens an expired link, the provider sends them back to the given return address. It SHALL fail with NotFound when the provider has no such account, and with Unavailable when the provider cannot be reached.

#### Scenario: Link is created

- **WHEN** a link is requested for an account
- **THEN** CreateOnboardingLink returns a new link that returns the Organizer to the given address when done

#### Scenario: Provider unreachable

- **WHEN** the provider cannot be reached
- **THEN** CreateOnboardingLink fails with Unavailable
