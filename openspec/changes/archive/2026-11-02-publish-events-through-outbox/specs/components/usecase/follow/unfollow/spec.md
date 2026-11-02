## REMOVED Requirements

### Requirement: Unfollow removes the Follow and announces it
**Reason**: Follow.Unfollow announces a removed Follow together with the removal (components/entity/follow/unfollow), so the usecase no longer announces, and an unfollow of an artist the fan does not follow is no longer announced.
**Migration**: Replaced by "Unfollow removes the Follow". Product analytics receives the "unfollow" signal from Follow.Unfollow's announcement, for removals only. A failure to announce now fails Unfollow and leaves the Follow in place.

## ADDED Requirements

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
