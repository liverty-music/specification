# Concert.FindEventsByVenueAndDate

## Purpose

Finds the Events already held at any of the given Venue and local date pairs, with the fields needed to decide identity and parentage.

## Requirements

### Requirement: Events at venue and date pairs

FindEventsByVenueAndDate SHALL return each Event whose Venue and local date equal one of the given pairs, once, with its id, Series, Venue, local date and start time. Given no pairs, or when no Event matches, it SHALL return an empty list without error.

#### Scenario: Two shows on one date
- **WHEN** Venue V has Events on 2026-06-01 at 13:00 and 18:00 and the pair (V, 2026-06-01) is given
- **THEN** both Events are returned

#### Scenario: No match
- **WHEN** no Event is held at any given pair
- **THEN** an empty list is returned
