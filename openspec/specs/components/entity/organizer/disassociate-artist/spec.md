# Organizer.DisassociateArtist

## Purpose

Removes the link between an Organizer and one Artist it represents.

## Requirements

### Requirement: DisassociateArtist is idempotent

DisassociateArtist SHALL remove the link between the Organizer and the Artist, after which the Artist can be linked to any Organizer. It SHALL succeed and change nothing when no such link exists.

#### Scenario: Linked Artist

- **WHEN** the Artist is linked to the Organizer
- **THEN** the link is removed and the Artist is free to be associated again

#### Scenario: No link

- **WHEN** the Artist is not linked to the Organizer
- **THEN** DisassociateArtist succeeds and nothing changes
