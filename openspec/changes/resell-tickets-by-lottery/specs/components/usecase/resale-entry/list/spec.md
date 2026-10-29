# Spec Delta

## Purpose

ResaleEntryUseCase.List returns the signed-in fan's official resale entries and the time of the next draw of each Entered one.

## ADDED Requirements

### Requirement: The fan's entries

List SHALL return the signed-in fan's ResaleEntries from ResaleEntry.ListByUser, each with its TicketStock, its SeatType and, for an Entered entry, the time of its event's next draw.

#### Scenario: Entered entry
- **WHEN** a fan with an Entered entry for an event on 10 November lists their entries at 15:00 on 5 November
- **THEN** the entry is returned with its next draw at 12:00 on 6 November

#### Scenario: No entries
- **WHEN** the fan never applied
- **THEN** the list is empty
