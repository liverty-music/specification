## ADDED Requirements

### Requirement: Similar artists listed only by name are offered when registered
When the similar-artist list names an artist without an MBID, ArtistUseCase.ListSimilar SHALL offer the registered artist that alone has that name, in the catalog's name or one of its aliases, so a fan finds an artist the listing service files under a romanized name.

#### Scenario: Romanized name
- **WHEN** a fan looks at artists similar to a seed, the listing includes `Yorushika` without an MBID, and `ヨルシカ` is registered and offered to fans
- **THEN** the similar artists include `ヨルシカ`

#### Scenario: Not registered
- **WHEN** the listing includes a name without an MBID that no registered artist has
- **THEN** no artist is added for it
