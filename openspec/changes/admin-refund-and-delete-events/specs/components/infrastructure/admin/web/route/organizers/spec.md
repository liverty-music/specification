## ADDED Requirements

### Requirement: An admin creates a test Artist for the Organizer

A provisioning or active Organizer's detail SHALL offer `Create test artist` beside the artist search, with a name field. A test Artist has a name the admin chooses and a music-catalog id the screen generates at random, so it matches no real artist. Under the field the screen SHALL show `Use a name no real artist uses.` On submit, the screen SHALL register the Artist with ArtistService.Create, then associate it with the Organizer with OrganizerService.AssociateArtist, and show it in the roster. When the association fails after the Artist was registered, the screen SHALL keep that Artist and offer to retry only the association, so a retry registers no second Artist. An empty name SHALL be refused by the screen without a call. A deactivated Organizer's detail SHALL NOT offer `Create test artist`.

#### Scenario: Test artist created and associated

- **WHEN** the admin enters `E2E Test Artist` for an active Organizer and submits
- **THEN** ArtistService.Create is called once with that name and a generated music-catalog id, the Artist is associated with the Organizer, and the roster lists `E2E Test Artist`

#### Scenario: Association fails after registration

- **WHEN** ArtistService.Create succeeds and OrganizerService.AssociateArtist fails with Unavailable
- **THEN** the screen shows an error and offers to retry the association, and retrying calls only OrganizerService.AssociateArtist for the same Artist

#### Scenario: Empty name

- **WHEN** the admin submits `Create test artist` with an empty name
- **THEN** no call is made and the field asks for a name

### Requirement: A represented Artist opens its concerts

Each Artist in the selected Organizer's roster SHALL link to the Artist concerts screen for that Artist, whatever the Organizer's status.

#### Scenario: Open an artist's concerts

- **WHEN** the admin activates the link of a represented Artist
- **THEN** the Artist concerts screen opens for that Artist
