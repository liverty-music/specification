# Unfollow

## Purpose

Manage the relationship between users and artists they follow, including follow/unfollow actions and listing followed artists.

## Requirements

### Requirement: Idempotent Unfollow Logic
The system SHALL allow users to unfollow artists, ensuring that the operation is idempotent. The use case layer SHALL resolve the external identity to the internal user UUID before deleting from `followed_artists`.

#### Scenario: Unfollowing an artist
- **WHEN** a user requests to unfollow an artist they currently follow
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID
- **AND** the system SHALL remove the corresponding record from the `followed_artists` table
