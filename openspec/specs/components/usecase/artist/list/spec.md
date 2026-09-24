# ArtistUseCase.List

## Purpose

ArtistUseCase.List returns every registered artist, for catalog-wide views of the artists Liverty Music knows.

## Requirements

### Requirement: List returns all registered artists
ArtistUseCase.List SHALL return what Artist.List returns and SHALL return its error unchanged.

#### Scenario: Artists registered
- **WHEN** List is called and artists are registered
- **THEN** every registered artist is returned

#### Scenario: Store failure
- **WHEN** Artist.List fails with Internal
- **THEN** List fails with Internal
