## MODIFIED Requirements

### Requirement: Artist images are kept current
An artist's images SHALL be checked again by the daily image run once its last check is more than 7 days old, while at least one fan follows the artist or the artist performs at a Concert. An artist that nobody follows and that performs at no Concert SHALL keep the images of its last check. An artist registered through ArtistUseCase.Create, which makes no announcement, SHALL get its first image check from the daily image run.

#### Scenario: Stale images
- **WHEN** a followed artist's images were last checked 8 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist nobody follows
- **WHEN** an artist found by a search was checked when it was registered, nobody follows it and it performs at no Concert
- **THEN** the daily image run does not check its images again

#### Scenario: Artist followed later
- **WHEN** a fan follows an artist whose images were last checked 30 days ago
- **THEN** the next daily image run checks them again and records the result

#### Scenario: Artist registered directly
- **WHEN** an artist is registered through ArtistUseCase.Create
- **THEN** its images are first checked by the next daily image run
