# Follow an artist

## Purpose

A fan follows an artist and the follow takes effect at once; when the platform has never looked for that artist's concerts, a first concert search starts in the background, so the artist's upcoming concerts reach the catalog and the fan's Dashboard without the fan waiting for it.

## Requirements

### Requirement: The follow is answered before any background work

When a signed-in fan follows an artist, FollowUseCase.Follow SHALL answer as soon as the Follow is stored; the artist SHALL show as followed at once, and nothing that happens in the background afterwards SHALL undo or fail the follow.

#### Scenario: Fan follows from Discovery

- **WHEN** a signed-in fan taps an artist on Discovery
- **THEN** the artist shows as followed at once and appears in My Artists at hype level Nearby

#### Scenario: Background search fails

- **WHEN** a fan follows an artist that has never been searched and the concert search fails
- **THEN** the fan still follows the artist and no error is shown

### Requirement: A first follow of a never-searched artist starts a concert search

When the followed artist has never been searched, FollowUseCase.Follow SHALL start ConcertUseCase.SearchNewConcerts for it in the background, and the concerts the search finds SHALL reach the catalog as the story stories/discover-new-concerts describes. When the artist has been searched before, following it SHALL start no search. The fan's app SHALL never start a concert search itself after a follow.

#### Scenario: Never-searched artist with announced concerts

- **WHEN** a fan follows an artist that has never been searched, and the search finds two newly announced concerts at known venues
- **THEN** once the search completes, both concerts are in the catalog and appear on the fan's Dashboard

#### Scenario: Artist searched before

- **WHEN** a fan follows an artist that another fan followed yesterday
- **THEN** no concert search starts and the fan's Dashboard shows the artist's concerts already in the catalog

#### Scenario: Several fans follow a new artist at once

- **WHEN** two fans follow the same never-searched artist a few seconds apart
- **THEN** the artist's concerts are stored once, not twice

### Requirement: Discovery tells the fan the artist has upcoming concerts

After a follow on Discovery, the Discovery screen SHALL look up the artist's concerts already in the catalog and, when it has any, tell the fan that the artist has upcoming events.

#### Scenario: Artist with upcoming concerts

- **WHEN** a fan follows an artist on Discovery that has upcoming concerts in the catalog
- **THEN** a message says the artist has upcoming events

#### Scenario: Artist without concerts yet

- **WHEN** a fan follows an artist on Discovery that has no concerts in the catalog
- **THEN** no such message is shown

### Requirement: The follow fills in the artist's official site

When the followed artist has no official site and the music catalog lists one, the site SHALL be stored for the artist after the follow, so later ticket-sale discovery can use it.

#### Scenario: Artist without an official site

- **WHEN** a fan follows an artist that has no official site and the music catalog lists its homepage
- **THEN** the artist's official site is that homepage shortly after the follow
