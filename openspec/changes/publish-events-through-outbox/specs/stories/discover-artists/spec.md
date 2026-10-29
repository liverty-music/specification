## MODIFIED Requirements

### Requirement: Artist images are kept current
An artist's images SHALL be checked again by the daily image run once its last check is more than 7 days old. An artist registered through ArtistUseCase.Create is announced by Artist.Create like any other registered artist, so its first image check follows that announcement.

#### Scenario: Stale images
- **WHEN** an artist's images were last checked 8 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist registered directly
- **WHEN** an artist is registered through ArtistUseCase.Create
- **THEN** its images are first checked once its announcement is handled
