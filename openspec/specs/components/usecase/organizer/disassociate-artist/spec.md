# OrganizerUseCase.DisassociateArtist

## Purpose

OrganizerUseCase.DisassociateArtist removes an Artist from an Organizer's roster, freeing the Artist to be associated with another Organizer.

## Requirements

### Requirement: DisassociateArtist unlinks the Artist from a changeable roster

DisassociateArtist SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist, and SHALL fail with FailedPrecondition when the Organizer's roster is fixed because it is deactivated. It SHALL then remove the link through Organizer.DisassociateArtist, succeeding when the Artist was not linked.

#### Scenario: Disassociate frees the Artist

- **WHEN** an Artist represented by the Organizer is disassociated
- **THEN** the link is removed and the Artist can be associated with another Organizer

#### Scenario: Artist not linked

- **WHEN** the Artist is not represented by the Organizer
- **THEN** DisassociateArtist succeeds and nothing changes

#### Scenario: Deactivated Organizer

- **WHEN** the Organizer is deactivated
- **THEN** DisassociateArtist fails with FailedPrecondition

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** DisassociateArtist fails with NotFound
