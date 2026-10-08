# Spec Delta

## MODIFIED Requirements

### Requirement: Only admins manage Organizers

Every request SHALL carry a valid sign-in, or fail with Unauthenticated, and the caller SHALL hold the admin role, or the request fails with PermissionDenied and has no effect.

#### Scenario: Not signed in

- **WHEN** a request has no valid sign-in
- **THEN** it fails with Unauthenticated

#### Scenario: Non-admin cannot create an Organizer

- **WHEN** a caller without the admin role calls Create
- **THEN** it fails with PermissionDenied and no Organizer is created

#### Scenario: Non-admin cannot list Organizers

- **WHEN** a caller without the admin role calls List or Get
- **THEN** it fails with PermissionDenied

#### Scenario: Non-admin sets a rate

- **WHEN** a caller without the admin role calls SetPlatformFeeRate
- **THEN** it fails with PermissionDenied and the rate is unchanged

### Requirement: Requests are validated before any usecase runs

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- a required OrganizerId or ArtistId is missing or malformed;
- Create's name is not 1 to 200 characters;
- Create's operator email is not an email address;
- any of UpdateSellerDetails' seller details is missing;
- SetPlatformFeeRate's rate is missing.

#### Scenario: Name too long

- **WHEN** Create is called with a 201-character name
- **THEN** it fails with InvalidArgument and no Organizer is created

#### Scenario: Malformed operator email

- **WHEN** Create is called with an operator email that is not an email address
- **THEN** it fails with InvalidArgument

#### Scenario: Missing OrganizerId

- **WHEN** Get, ListArtists, AssociateArtist, DisassociateArtist, Deactivate, UpdateSellerDetails or SetPlatformFeeRate is called without an OrganizerId
- **THEN** it fails with InvalidArgument

#### Scenario: Missing rate

- **WHEN** SetPlatformFeeRate is called without a rate
- **THEN** it fails with InvalidArgument and the rate is unchanged

### Requirement: Each call runs one OrganizerUseCase method

Each call SHALL run one usecase method:
- Create SHALL run OrganizerUseCase.Create and return the created Organizer.
- Get, List and ListArtists SHALL run OrganizerUseCase.Get, OrganizerUseCase.List and OrganizerUseCase.ListArtists for any Organizer the admin names.
- AssociateArtist, DisassociateArtist, Deactivate, UpdateSellerDetails and SetPlatformFeeRate SHALL run the usecase method of the same name.

Errors from the usecase SHALL be returned unchanged. An Organizer is returned with its id, name, seller details and platform fee rate.

#### Scenario: Admin lists Organizers and inspects a roster

- **WHEN** an admin lists Organizers and then requests one Organizer's Artists
- **THEN** it returns every Organizer, and then the Artists that Organizer represents

#### Scenario: Admin reads any Organizer

- **WHEN** an admin calls Get for a deactivated Organizer
- **THEN** it returns that Organizer's id, name, seller details and platform fee rate

#### Scenario: Admin records seller details

- **WHEN** an admin calls UpdateSellerDetails with complete details
- **THEN** OrganizerUseCase.UpdateSellerDetails runs and the Organizer is returned with them
