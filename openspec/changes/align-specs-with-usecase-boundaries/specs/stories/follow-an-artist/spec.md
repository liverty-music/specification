# Spec Delta

## MODIFIED Requirements

### Requirement: A first follow of a never-searched artist starts a concert search

When a fan newly follows an artist, FollowUseCase.Follow SHALL announce the follow, and on that announcement ConcertUseCase.SearchNewConcertsOnFirstFollow SHALL start ConcertUseCase.SearchNewConcerts for the artist when it has never been searched; the concerts the search finds SHALL reach the catalog as the story stories/discover-new-concerts describes. When the artist has been searched before, following it SHALL start no search. When the follow cannot be announced, no search SHALL start on that follow, and the artist's concerts reach the catalog through the daily concert search at 18:00 JST. The fan's app SHALL never start a concert search itself after a follow.

#### Scenario: Never-searched artist with announced concerts

- **WHEN** a fan follows an artist that has never been searched, and the search finds two newly announced concerts at known venues
- **THEN** once the search completes, both concerts are in the catalog and appear on the fan's Dashboard

#### Scenario: Artist searched before

- **WHEN** a fan follows an artist that another fan followed yesterday
- **THEN** no concert search starts and the fan's Dashboard shows the artist's concerts already in the catalog

#### Scenario: Several fans follow a new artist at once

- **WHEN** two fans follow the same never-searched artist a few seconds apart
- **THEN** the artist's concerts are stored once, not twice

#### Scenario: Follow not announced

- **WHEN** a fan follows a never-searched artist and the follow cannot be announced
- **THEN** the fan still follows the artist, no concert search starts on that follow, and the artist is searched in the next daily concert search
