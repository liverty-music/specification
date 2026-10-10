# Spec Delta

## MODIFIED Requirements

### Requirement: Concert with an event page

Get SHALL take an Event id and read the Concert with Concert.ListByIDs, with its Venue, performers, publish state and Series, and the Series with Series.Get. When the Event has an event page (see Series), Get SHALL return the Concert with its own publish state and its Series' description, cover image, visibility and publish state. Get needs no signed-in caller.

#### Scenario: Published public concert

- **WHEN** Get is called for a PUBLISHED Event of a PUBLIC first-party Series
- **THEN** it returns the Concert with publish state PUBLISHED and its Series' description and cover image

#### Scenario: Cancelled series

- **WHEN** Get is called for a CANCELLED Event of a PUBLIC first-party Series
- **THEN** it returns the Concert with publish state CANCELLED

#### Scenario: Draft date of a published series

- **WHEN** Get is called for a DRAFT Event of a PUBLIC first-party Series whose other Events are PUBLISHED
- **THEN** it fails with NotFound, exactly as for an unknown id
