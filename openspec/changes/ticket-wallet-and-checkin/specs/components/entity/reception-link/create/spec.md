# Spec Delta

## Purpose

Stores a new ReceptionLink for an event.

## ADDED Requirements

### Requirement: Create stores a new link

Create SHALL store a new Unused ReceptionLink for the given event with the given name and return it with its token. It SHALL fail with InvalidArgument when the name is invalid, and with AlreadyExists when another link of the same event that is not Revoked has the same name after trimming.

#### Scenario: New link stored

- **WHEN** a link named `受付A` is created for an event that has no link
- **THEN** an Unused link named `受付A` is stored and returned with its token

#### Scenario: Duplicate name

- **WHEN** the event has an InUse link named `受付A` and another `受付A` is created
- **THEN** Create fails with AlreadyExists and nothing is stored

#### Scenario: Name of a revoked link reused

- **WHEN** the event's only link named `受付A` is Revoked and a new `受付A` is created
- **THEN** the new link is stored
