## ADDED Requirements

### Requirement: A new representation is announced with the change

When AssociateArtist links an Artist to the Organizer, it SHALL announce the Artist, with the Organizer as its organizer, together with the link: both are stored or neither is. When it fails, including with AlreadyExists, it SHALL announce nothing. When the announcement cannot be recorded, AssociateArtist SHALL fail with Unavailable and the Artist SHALL stay unrepresented.

#### Scenario: Unrepresented Artist linked

- **WHEN** the Artist is linked to no Organizer and AssociateArtist is called
- **THEN** the Artist is announced once, with the Organizer as its organizer

#### Scenario: Artist already represented

- **WHEN** the Artist is already linked to an Organizer
- **THEN** AssociateArtist fails with AlreadyExists and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the Artist is linked to no Organizer and the announcement cannot be recorded
- **THEN** AssociateArtist fails with Unavailable and the Artist is linked to no Organizer
