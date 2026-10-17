# components/entity/organizer/send-sign-in-links Specification

## Purpose
Sends one email to an address with a sign-in link for each of the given Organizers, each link opening the organizer console tied to that Organizer's Organization.

## Requirements

### Requirement: SendSignInLinks emails one link per Organizer

SendSignInLinks SHALL send one email, in Japanese, to the given address, listing each given Organizer by name with one link to the organizer console that names that Organizer's Organization by its short name (`https://organizer.liverty-music.app/?org=<short name>`). The email SHALL say that it was requested from the organizer console and can be ignored when the recipient did not request it. Any failure to send SHALL fail with Internal.

#### Scenario: Two Organizers

- **WHEN** SendSignInLinks runs for `band@example.com` with the Organizers XX Records and YY Promotion
- **THEN** one email reaches `band@example.com` naming both, each with its own sign-in link

#### Scenario: Mail service unavailable

- **WHEN** the email cannot be handed to the mail service
- **THEN** SendSignInLinks fails with Internal
