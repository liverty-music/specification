# Unfollow

## Purpose

FollowUseCase.Unfollow ends a fan's Follow of an artist through Follow.Unfollow, which announces the ended follow, so the fan no longer receives pushes about that artist's new concerts.

## Requirements

### Requirement: Unfollow removes the Follow

Unfollow SHALL remove the fan's Follow of the artist through Follow.Unfollow and succeed, also when the fan did not follow it. When Follow.Unfollow fails, Unfollow SHALL fail with that error.

#### Scenario: Fan unfollows an artist

- **WHEN** a fan unfollows an artist they follow
- **THEN** the Follow is removed and Unfollow succeeds

#### Scenario: Artist not followed

- **WHEN** a fan unfollows an artist they do not follow
- **THEN** Unfollow succeeds and nothing is removed

#### Scenario: Removal fails

- **WHEN** Follow.Unfollow fails with Unavailable
- **THEN** Unfollow fails with Unavailable and the Follow remains
