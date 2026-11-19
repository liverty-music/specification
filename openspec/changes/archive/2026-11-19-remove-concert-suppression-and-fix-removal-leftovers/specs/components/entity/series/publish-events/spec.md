## REMOVED Requirements

### Requirement: Blocked slots fail the whole publish
**Reason**: Suppression is retired, so the requirement's statement and scenario about a suppressed slot go; the rest moves unchanged to "Held slots fail the whole publish".
**Migration**: See "Held slots fail the whole publish".

## ADDED Requirements

### Requirement: Held slots fail the whole publish

PublishEvents SHALL fail with FailedPrecondition, changing nothing, when any given Event's slot is held by an Event of another first-party Series, whether that Series belongs to another Organizer or to the same one, or by a CANCELLED Event.

#### Scenario: Another Organizer's slot
- **WHEN** one given DRAFT Event's slot holds an Event of another Organizer's Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Slot of another Series of the same Organizer
- **WHEN** one given DRAFT Event's slot holds a PUBLISHED Event of another Series of the same Organizer, with its own visibility, SeatTypes and TicketSales
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT, and the held Event stays in its Series with its visibility, SeatTypes and TicketSales unchanged

#### Scenario: Cancelled slot
- **WHEN** one given DRAFT Event's slot holds a CANCELLED Event
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT
