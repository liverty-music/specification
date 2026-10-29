# Spec Delta

## MODIFIED Requirements

### Requirement: Corrections keep what publish fixed

Update SHALL read the Series with its Events (Series.GetAuthored) and fail with FailedPrecondition, changing nothing, when:
- a PUBLISHED or CANCELLED Event of the Series is not given, because a published date is cancelled, not removed;
- a given PUBLISHED Event's venue, date or per-account limit differs from the Event's;
- a given CANCELLED Event differs from the Event in any value;
- the Series has a PUBLISHED or CANCELLED Event and the given type, source page or visibility differ from the Series';
- a given PUBLISHED Event's start time differs from the Event's and TicketSale.ListByEvent returns at least one sale for the Event.

#### Scenario: Published venue changed
- **WHEN** the owner gives a PUBLISHED Event with another venue
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published per-account limit changed
- **WHEN** the owner gives a PUBLISHED Event whose per-account limit is 4 with a limit of 2
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published date left out
- **WHEN** the owner updates a Series and leaves out one of its PUBLISHED Events
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Visibility changed after publish
- **WHEN** the owner changes a Series with a PUBLISHED Event from PUBLIC to UNLISTED
- **THEN** Update fails with FailedPrecondition

#### Scenario: Start time on sale
- **WHEN** the owner changes the start time of a PUBLISHED Event that a TicketSale names
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Start time before any sale
- **WHEN** the owner sets the start time of a PUBLISHED Event that no TicketSale names
- **THEN** the start time is set
