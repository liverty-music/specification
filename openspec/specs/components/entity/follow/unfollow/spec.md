# Follow.Unfollow

## Purpose

Removes the Follow of one artist by one fan, leaving the fan's other Follows and other fans' Follows of the artist in place.

## Requirements

### Requirement: Unfollow removes only that pair and is idempotent

Unfollow SHALL remove the Follow for the given fan and artist and nothing else. When the fan does not follow the artist, Unfollow SHALL succeed and change nothing.

#### Scenario: Unfollow a followed artist

- **WHEN** the fan follows artists A and B and Unfollow is called for A
- **THEN** the Follow of A is removed and the Follow of B remains

#### Scenario: Unfollow an artist not followed

- **WHEN** the fan does not follow the artist
- **THEN** Unfollow succeeds and nothing changes
