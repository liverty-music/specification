# Unfollow

## Purpose

FollowUseCase.Unfollow ends a fan's Follow of an artist, so the fan no longer receives pushes about that artist's new concerts, and announces the unfollow.

## Requirements

### Requirement: Unfollow removes the Follow and announces it

Unfollow SHALL remove the fan's Follow of the artist through Follow.Unfollow and then announce that the fan unfollowed the artist, also when the fan did not follow it. A failure to remove SHALL fail Unfollow with that error and announce nothing; a failure to announce SHALL NOT fail Unfollow.

#### Scenario: Fan unfollows an artist

- **WHEN** a fan unfollows an artist they follow
- **THEN** the Follow is removed, the unfollow is announced, and Unfollow succeeds

#### Scenario: Artist not followed

- **WHEN** a fan unfollows an artist they do not follow
- **THEN** Unfollow succeeds, nothing is removed, and the unfollow is announced

#### Scenario: Announcement fails

- **WHEN** the Follow is removed but announcing fails
- **THEN** Unfollow still succeeds
