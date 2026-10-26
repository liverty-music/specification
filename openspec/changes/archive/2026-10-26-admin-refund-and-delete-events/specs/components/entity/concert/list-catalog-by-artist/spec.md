## Purpose

Concert.ListCatalogByArtist returns every Concert one Artist performs in, in every publish state but DRAFT, so an admin can manage that Artist's Concerts. Unlike Concert.ListByArtist it does not leave out what fans cannot see.

## ADDED Requirements

### Requirement: One artist's catalog, oldest first

ListCatalogByArtist SHALL return every Concert whose performers include the Artist — past and upcoming, of every Series whatever its visibility, CANCELLED ones included — ordered by local date ascending, each with its Venue, Series, performers and publish state. DRAFT Events and ConcertCandidates are not Concerts and SHALL NOT be returned. An Artist that performs in no Concert, or an id no Artist has, SHALL yield an empty list. ListCatalogByArtist SHALL fail with InvalidArgument when no Artist is given.

#### Scenario: Narrowed to one artist
- **WHEN** the Artist A performs in a PUBLISHED Concert of an UNLISTED Series and in a CANCELLED Concert, another Artist performs in a third Concert, and ListCatalogByArtist is given A
- **THEN** only A's two Concerts are returned, oldest first

#### Scenario: Artist without concerts
- **WHEN** ListCatalogByArtist is given an Artist that performs in no Concert
- **THEN** it returns an empty list

#### Scenario: Draft event excluded
- **WHEN** the Artist performs at a DRAFT Event of a published Series
- **THEN** that Event is not returned

#### Scenario: No artist given
- **WHEN** ListCatalogByArtist is called with no Artist
- **THEN** it fails with InvalidArgument
