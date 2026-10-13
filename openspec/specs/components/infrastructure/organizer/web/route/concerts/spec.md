# Concerts

## Purpose

The organizer console's concert list: an Organizer's own concerts and events, with the actions available on each.

## Requirements

### Requirement: Organizer console entry point to lottery configuration

The organizer console SHALL provide a **discoverable navigation entry point** from
an Organizer's **published** event to that event's lottery sale configuration, so
an Organizer reaches the configure screen (and, once a sale exists, its status
screen) **without knowing the event's internal id or typing an address**. The entry
point SHALL be surfaced in the Organizer's own concert/event listing, SHALL open
the editor for that event, and SHALL be gated on the event being `PUBLISHED`
(a lottery sale is unavailable while the concert/Series is `DRAFT`). This closes
the gap where the lottery sale editor was reachable only by typing its
address.

#### Scenario: Organizer reaches lottery configuration from a published event

- **WHEN** an Organizer views one of their `PUBLISHED` events in the console
- **THEN** the console surfaces a "Configure lottery" action that opens the lottery sale editor for that event

#### Scenario: No lottery entry point for a draft event

- **WHEN** an Organizer views one of their `DRAFT` events in the console
- **THEN** the "Configure lottery" action is absent or disabled — a lottery sale requires a published event

### Requirement: Publish while a concert has draft dates

The concert list SHALL show each concert's derived publish state and SHALL offer Publish for a concert whenever it has at least one DRAFT event, published or not; Publish SHALL publish every DRAFT event of the concert. Cancel SHALL be offered while the concert has a PUBLISHED or DRAFT event.

#### Scenario: Published tour with a new date
- **WHEN** a PUBLISHED concert has one DRAFT event
- **THEN** the list shows the concert as Published and offers Publish, which publishes the DRAFT event

#### Scenario: Nothing left to publish
- **WHEN** every event of a concert is PUBLISHED or CANCELLED
- **THEN** Publish is not offered
