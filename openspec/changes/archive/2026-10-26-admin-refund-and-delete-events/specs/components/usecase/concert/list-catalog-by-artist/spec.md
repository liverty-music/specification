## Purpose

ConcertUseCase.ListCatalogByArtist gives an admin every Concert one Artist performs in, so the admin console can refund and delete that Artist's Concerts.

## ADDED Requirements

### Requirement: One artist's catalog for admins

ListCatalogByArtist SHALL take an Artist and return the result of Concert.ListCatalogByArtist for it unchanged, failing with InvalidArgument when no Artist is given.

#### Scenario: One artist's concerts
- **WHEN** ListCatalogByArtist is given an Artist that performs in a CANCELLED Organizer Concert
- **THEN** that Concert is returned

#### Scenario: Missing artist
- **WHEN** ListCatalogByArtist is called with no Artist
- **THEN** it fails with InvalidArgument and nothing is read
