# Spec Delta

## Purpose

Returns the active Organizers whose owner email is a given address, so the person who owns them can be sent a way to sign in to each.

## ADDED Requirements

### Requirement: ListByOwnerEmail returns the active Organizers for an email

ListByOwnerEmail SHALL return every active Organizer whose owner email equals the given address, compared without regard to letter case, ordered by name ascending, with each Organizer's provider organizer ID. It SHALL return an empty list when none matches; provisioning and deactivated Organizers are never returned.

#### Scenario: Owner of two Organizers

- **WHEN** two active Organizers have the owner email `band@example.com`
- **THEN** ListByOwnerEmail for `Band@Example.com` returns both, ordered by name

#### Scenario: Deactivated Organizer

- **WHEN** the only Organizer with the owner email is deactivated
- **THEN** ListByOwnerEmail returns an empty list

#### Scenario: Unknown email

- **WHEN** no Organizer has the owner email
- **THEN** ListByOwnerEmail returns an empty list
