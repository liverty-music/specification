## ADDED Requirements

### Requirement: A newly registered artist is announced with its registration

For each artist that Create registers, it SHALL announce the Artist as created, together with the registration: all are stored or none is. An artist whose MBID was already registered SHALL NOT be announced, also when another call registered it between the caller's lookup and this Create. When an announcement cannot be recorded, Create SHALL fail with Unavailable and register none of the new artists.

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
