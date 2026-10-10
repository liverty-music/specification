# Spec Delta

## REMOVED Requirements

### Requirement: A draft event exists only while its series is a draft

**Reason**: DraftEvent is removed. A performance being authored is an Event in the DRAFT state, and a published Series can hold DRAFT Events for dates it adds later.
**Migration**: Existing draft performances move into Events with the publish state DRAFT, keeping their ids, and their Series' draft performers become the performers of each of those Events. See `components/entity/event`, requirement "Publish state of an event".

### Requirement: A multi-showtime day is several draft events

**Reason**: DraftEvent is removed.
**Migration**: Each showtime is its own Event, as it already is for published performances (`components/entity/event`, "Event identity is venue, date and start time": matinee and evening shows are distinct Events).
