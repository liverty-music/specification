# TicketApplication.Get

## Purpose

Returns one TicketApplication by its id, in any state.

## Requirements

### Requirement: Get by id

Get SHALL return the application with the given id, including a Withdrawn one, and SHALL fail with NotFound when none exists.

#### Scenario: Existing application

- **WHEN** Get is called with the id of a stored application
- **THEN** that application is returned

#### Scenario: Unknown id

- **WHEN** no application has the id
- **THEN** Get fails with NotFound
