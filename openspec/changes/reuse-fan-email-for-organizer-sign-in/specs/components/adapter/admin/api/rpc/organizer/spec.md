# Spec Delta

## ADDED Requirements

### Requirement: Requests are validated before a usecase runs

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- a required OrganizerId or ArtistId is missing or malformed;
- Create's name is not 1 to 200 characters;
- Create's short name is missing or is not a valid short name in the terms of the Organizer entity;
- Create's owner email is not an email address of at most 165 characters;
- any of SetBusinessDetails' legal name, representative name, business address, business phone number and contact email is missing;
- SetPlatformFeeRate's rate is missing.

#### Scenario: Name too long

- **WHEN** Create is called with a 201-character name
- **THEN** it fails with InvalidArgument and no Organizer is created

#### Scenario: Malformed short name

- **WHEN** Create is called with the short name `XX Records`
- **THEN** it fails with InvalidArgument and no Organizer is created

#### Scenario: Malformed owner email

- **WHEN** Create is called with an owner email that is not an email address
- **THEN** it fails with InvalidArgument

#### Scenario: Missing OrganizerId

- **WHEN** Get, AssociateArtist, DisassociateArtist, Deactivate, SetBusinessDetails or SetPlatformFeeRate is called without an OrganizerId
- **THEN** it fails with InvalidArgument

#### Scenario: Missing rate

- **WHEN** SetPlatformFeeRate is called without a rate
- **THEN** it fails with InvalidArgument and the rate is unchanged

### Requirement: Each call runs one OrganizerUseCase method and returns the short name

Each call SHALL run one usecase method:
- Create SHALL run OrganizerUseCase.Create with the name, the short name and the owner email and return the created Organizer.
- Get and List SHALL run OrganizerUseCase.Get and OrganizerUseCase.List for any Organizer the admin names.
- AssociateArtist, DisassociateArtist, Deactivate, Delete, SetBusinessDetails and SetPlatformFeeRate SHALL run the usecase method of the same name.

The admin Organizer service SHALL NOT list an Organizer's Artists; the admin artist service does (ListByOrganizer). Errors from the usecase SHALL be returned unchanged. An Organizer is returned with its id, name, short name, legal name, representative name, business address, business phone number, contact email and platform fee rate.

#### Scenario: Admin lists Organizers and inspects a roster

- **WHEN** an admin lists Organizers and then requests one Organizer's Artists
- **THEN** it returns every Organizer with its short name, and the Artists that Organizer represents come from the admin artist service's ListByOrganizer, not from the Organizer service

#### Scenario: Admin reads any Organizer

- **WHEN** an admin calls Get for a deactivated Organizer
- **THEN** it returns that Organizer's id, name, short name, business details and platform fee rate

#### Scenario: Admin deletes a deactivated Organizer

- **WHEN** an admin calls Delete for a deactivated Organizer
- **THEN** OrganizerUseCase.Delete runs and the call succeeds with an empty response

#### Scenario: Delete refused

- **WHEN** OrganizerUseCase.Delete fails with FailedPrecondition
- **THEN** Delete fails with FailedPrecondition

#### Scenario: Admin records business details

- **WHEN** an admin calls SetBusinessDetails with all five business details
- **THEN** OrganizerUseCase.SetBusinessDetails runs and the Organizer is returned with them

#### Scenario: Short name already used

- **WHEN** OrganizerUseCase.Create fails with AlreadyExists for the short name
- **THEN** Create fails with AlreadyExists

## REMOVED Requirements

### Requirement: Requests are validated before any usecase runs

**Reason**: Create's field is the owner email and Create now takes the short name (see "Requests are validated before a usecase runs").
**Migration**: The proto field `CreateRequest.operator_email` becomes `owner_email` and `short_name` is added (design.md D6).

### Requirement: Each call runs one OrganizerUseCase method

**Reason**: Create passes the short name and every returned Organizer carries it (see "Each call runs one OrganizerUseCase method and returns the short name").
**Migration**: None.
