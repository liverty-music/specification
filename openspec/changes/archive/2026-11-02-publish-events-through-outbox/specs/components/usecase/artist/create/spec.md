## MODIFIED Requirements

### Requirement: Create reports registration failures
ArtistUseCase.Create SHALL return the error of Artist.Create unchanged, and SHALL fail with Internal when Artist.Create returns no artist. Create itself announces nothing: Artist.Create announces an artist it registers, together with storing it (components/entity/artist/create), so its images and canonical name are resolved from that announcement.

#### Scenario: Registration rejected
- **WHEN** Artist.Create fails with InvalidArgument
- **THEN** Create fails with InvalidArgument

#### Scenario: Nothing returned
- **WHEN** Artist.Create returns no artist without an error
- **THEN** Create fails with Internal

#### Scenario: No announcement
- **WHEN** Create registers a new artist
- **THEN** the artist is announced once, by Artist.Create, and Create makes no announcement of its own
