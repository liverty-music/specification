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

### Requirement: A new representation is announced with the change

When AssociateArtist links an Artist to the Organizer, it SHALL announce the Artist as represented (Artist.Represented), with the Organizer as its organizer, together with the link: both are stored or neither is. When it fails, including with AlreadyExists, it SHALL announce nothing. When the announcement cannot be recorded, AssociateArtist SHALL fail with Unavailable and the Artist SHALL stay unrepresented.

#### Scenario: Unrepresented Artist linked

- **WHEN** the Artist is linked to no Organizer and AssociateArtist is called
- **THEN** the Artist is announced once as represented, with the Organizer as its organizer

#### Scenario: Artist already represented

- **WHEN** the Artist is already linked to an Organizer
- **THEN** AssociateArtist fails with AlreadyExists and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the Artist is linked to no Organizer and the announcement cannot be recorded
- **THEN** AssociateArtist fails with Unavailable and the Artist is linked to no Organizer
