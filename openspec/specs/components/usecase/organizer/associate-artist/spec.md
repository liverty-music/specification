# Associate Artist

## Purpose

Links an artist to the single organizer authorized to represent it, excluding that artist from automated discovery once represented so the organizer's own event pages take precedence.

## Requirements

### Requirement: Associate an artist with at most one organizer

The system SHALL associate an Organizer with zero or more Artists, and each
Artist SHALL be represented by **at most one** Organizer. Associating an
Artist that does not exist SHALL be rejected (no create-on-demand);
associating an Artist already represented SHALL be rejected. An admin SHALL
be able to disassociate an Artist; reassignment is disassociate followed by
associate.

#### Scenario: A label organizer represents multiple artists

- **WHEN** an Organizer is associated with several existing Artists
- **THEN** all associated Artists SHALL be retrievable for that Organizer

#### Scenario: Associating a non-existent artist is rejected

- **WHEN** an admin associates an ArtistId that does not exist
- **THEN** the system SHALL reject it with a not-found error and SHALL NOT
  create the artist

#### Scenario: An artist cannot be claimed by a second organizer

- **WHEN** an Artist already represented by one Organizer is associated with
  a different Organizer
- **THEN** the system SHALL reject it with an already-exists error

#### Scenario: Disassociate frees the artist

- **WHEN** an admin disassociates an Artist from its Organizer
- **THEN** the association SHALL be removed and the Artist SHALL be
  associable to another Organizer

### Requirement: Represented artists are excluded from scraping

While an artist is associated with an organizer, the system SHALL exclude
that artist from concert-search scraping (first-party is authoritative). The
exclusion SHALL be keyed on the **Organizer↔Artist association**, not on the
existence of a published concert: associating an artist starts the
exclusion, and disassociating it (or deactivating the organizer) resumes
scraping.

#### Scenario: Associated artist is excluded from discovery scraping

- **WHEN** the discovery pipeline runs for an artist associated with an
  active organizer
- **THEN** the system SHALL skip scraping that artist's concerts

#### Scenario: Disassociation resumes scraping

- **WHEN** an artist is disassociated from its organizer (or the organizer
  is deactivated)
- **THEN** the system SHALL resume scraping that artist's concerts
