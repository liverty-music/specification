# TicketApplication.UpdateState

## Purpose

Sets the state of one TicketApplication; it changes no other attribute.

## Requirements

### Requirement: Update the state

UpdateState SHALL set the application's state to the given state and SHALL fail with NotFound when no application has the id.

#### Scenario: State changed

- **WHEN** UpdateState sets an Applied application to Withdrawn
- **THEN** the application's state is Withdrawn and its other attributes are unchanged

#### Scenario: Unknown id

- **WHEN** no application has the id
- **THEN** UpdateState fails with NotFound
