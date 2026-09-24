# Organizer.AssociateArtist

## Purpose

Links an Artist to the Organizer that represents it, keeping each Artist with at most one Organizer.

## Requirements

### Requirement: AssociateArtist gives an Artist at most one Organizer

AssociateArtist SHALL link the Artist to the Organizer. It SHALL fail with AlreadyExists, and change nothing, when the Artist is already linked to any Organizer, the same one included. It does not check the status of the Organizer; that the Organizer and the Artist exist is the caller's concern.

#### Scenario: Unrepresented Artist

- **WHEN** the Artist is linked to no Organizer
- **THEN** the Artist becomes represented by the Organizer

#### Scenario: Artist already represented

- **WHEN** the Artist is already linked to an Organizer
- **THEN** AssociateArtist fails with AlreadyExists and the existing link is kept
