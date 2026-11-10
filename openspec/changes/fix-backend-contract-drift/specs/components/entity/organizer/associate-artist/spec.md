## MODIFIED Requirements

### Requirement: AssociateArtist gives an Artist at most one Organizer

AssociateArtist SHALL link the Artist to the Organizer. It SHALL fail with AlreadyExists, and change nothing, when the Artist is already linked to any Organizer, the same one included. It SHALL fail with FailedPrecondition, and change nothing, when the Organizer is deactivated, judged in the same step as the link, so a deactivation stored before the link is never missed. That the Organizer and the Artist exist is the caller's concern.

#### Scenario: Unrepresented Artist

- **WHEN** the Artist is linked to no Organizer
- **THEN** the Artist becomes represented by the Organizer

#### Scenario: Artist already represented

- **WHEN** the Artist is already linked to an Organizer
- **THEN** AssociateArtist fails with AlreadyExists and the existing link is kept

#### Scenario: Organizer deactivated just before the link

- **WHEN** the Organizer was active when its caller read it, and is deactivated before AssociateArtist links the Artist
- **THEN** AssociateArtist fails with FailedPrecondition and the Artist stays unrepresented
