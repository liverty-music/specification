# Artist.Create

## Purpose

Registers one or more artists by MBID and returns the registered artist for each, whether it was new or already known.

## Requirements

### Requirement: Create registers each MBID once
Create SHALL register every given artist whose MBID is not yet registered and SHALL return, for each given artist in input order, the registered artist with that MBID. An artist whose MBID is already registered SHALL be returned as registered, unchanged, and SHALL NOT be registered a second time. A new artist SHALL keep the id it was given, or get a fresh id when it has none.

#### Scenario: New MBID
- **WHEN** Create is called with an artist whose MBID is not registered
- **THEN** the artist is registered and returned

#### Scenario: Known MBID
- **WHEN** Create is called with an artist whose MBID is already registered under another name
- **THEN** the already registered artist is returned with its existing id and name, and nothing new is registered

#### Scenario: Mixed input keeps order
- **WHEN** Create is called with a known artist followed by a new artist
- **THEN** the result lists the known artist first and the new artist second

#### Scenario: Empty input
- **WHEN** Create is called with no artists
- **THEN** it returns an empty list and registers nothing

### Requirement: Create rejects an artist without a valid MBID
Create SHALL fail with InvalidArgument and register nothing when any given artist has no MBID or an MBID that is not 36 characters long.

#### Scenario: Artist without MBID
- **WHEN** Create is called with two artists and one has no MBID
- **THEN** Create fails with InvalidArgument and neither artist is registered

#### Scenario: Malformed MBID
- **WHEN** Create is called with an artist whose MBID is not 36 characters long
- **THEN** Create fails with InvalidArgument and nothing is registered

### Requirement: Create is all or nothing
Create SHALL register all of the new artists in one call or none of them; any other failure SHALL be reported as Internal or Unavailable.

#### Scenario: Store failure
- **WHEN** the artists cannot be stored
- **THEN** Create fails and none of the new artists is registered

### Requirement: A newly registered artist is announced with its registration

For each artist that Create registers, it SHALL announce the Artist as created (Artist.Created), together with the registration: all are stored or none is. An artist whose MBID was already registered SHALL NOT be announced, also when another call registered it between the caller's lookup and this Create. When an announcement cannot be recorded, Create SHALL fail with Unavailable and register none of the new artists.

#### Scenario: New MBID

- **WHEN** Create registers an artist whose MBID was not registered
- **THEN** one artist creation is announced, carrying that Artist

#### Scenario: Known MBID

- **WHEN** Create is called with an artist whose MBID is already registered
- **THEN** the registered artist is returned and nothing is announced

#### Scenario: Registered by a concurrent call

- **WHEN** two calls of Create are given the same unregistered MBID at the same time
- **THEN** the artist is registered once and announced once

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would register a new artist and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and no new artist is registered
