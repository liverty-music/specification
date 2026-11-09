# Follow.ListAll

## Purpose

Returns every artist that at least one fan follows, the set the daily discovery jobs go through.

## Requirements

### Requirement: Each followed artist once

ListAll SHALL return each artist that has at least one Follow exactly once, with its id, name, MBID (empty when the artist has none) and activity_ended, in no guaranteed order. An artist nobody follows SHALL NOT be returned. When nobody follows any artist, ListAll SHALL return an empty list.

#### Scenario: Artist followed by two fans

- **WHEN** two fans follow the same artist
- **THEN** that artist is returned once

#### Scenario: Unfollowed artist

- **WHEN** an artist's last follower unfollows it
- **THEN** the artist is no longer returned

#### Scenario: No follows

- **WHEN** no fan follows any artist
- **THEN** ListAll returns an empty list

#### Scenario: Followed artist whose activity has ended

- **WHEN** a fan follows an artist whose activity_ended is true
- **THEN** ListAll returns the artist with activity_ended true
