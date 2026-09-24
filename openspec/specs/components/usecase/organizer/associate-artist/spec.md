# OrganizerUseCase.AssociateArtist

## Purpose

OrganizerUseCase.AssociateArtist links an existing Artist to an Organizer so the Organizer represents it. Each Artist can be represented by at most one Organizer, so reassigning an Artist is DisassociateArtist followed by AssociateArtist.

## Requirements

### Requirement: AssociateArtist links an existing Artist to a changeable roster

AssociateArtist SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist, and SHALL fail with FailedPrecondition when the Organizer's roster is fixed because it is deactivated. It SHALL load the Artist through Artist.Get, failing with NotFound when it does not exist; it never creates an Artist. It SHALL then link them through Organizer.AssociateArtist, failing with AlreadyExists when the Artist is already represented. An Organizer that is still provisioning can be given Artists.

#### Scenario: A label represents several Artists

- **WHEN** several existing Artists are associated with one active Organizer
- **THEN** the Organizer represents all of them

#### Scenario: Unknown Artist

- **WHEN** the Artist does not exist
- **THEN** AssociateArtist fails with NotFound and no Artist is created

#### Scenario: Artist claimed by another Organizer

- **WHEN** the Artist is already represented by another Organizer
- **THEN** AssociateArtist fails with AlreadyExists

#### Scenario: Deactivated Organizer

- **WHEN** the Organizer is deactivated
- **THEN** AssociateArtist fails with FailedPrecondition and nothing is linked

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** AssociateArtist fails with NotFound

### Requirement: A new association is announced

When the Artist is linked, AssociateArtist SHALL announce that the Organizer now represents the Artist. A failure to announce SHALL NOT fail AssociateArtist.

#### Scenario: Announcement fails

- **WHEN** the link is stored but the announcement cannot be made
- **THEN** AssociateArtist still succeeds and the link is kept
