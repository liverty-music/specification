# Concerts

## Purpose

The organizer console's concert list: an Organizer's own concerts and events, with the actions available on each.

## Requirements

### Requirement: Organizer console entry point to lottery configuration

The organizer console SHALL provide a **discoverable navigation entry point** from
an Organizer's **published** event to that event's lottery-phase configuration, so
an Organizer reaches the configure screen (and, once a phase exists, its status
screen) **without knowing the internal `eventId` or typing a URL**. The entry
point SHALL be surfaced in the Organizer's own concert/event listing, SHALL carry
the `eventId` automatically, and SHALL be gated on the event being `PUBLISHED`
(a lottery phase is unavailable while the concert/Series is `DRAFT`). This closes
the gap where the `lottery/configure/:eventId` route was reachable only by direct
URL entry.

#### Scenario: Organizer reaches lottery configuration from a published event

- **WHEN** an Organizer views one of their `PUBLISHED` events in the console
- **THEN** the console surfaces a "Configure lottery" action that navigates to that event's lottery-phase configuration, carrying the `eventId` automatically

#### Scenario: No lottery entry point for a draft event

- **WHEN** an Organizer views one of their `DRAFT` events in the console
- **THEN** the "Configure lottery" action is absent or disabled — a lottery phase requires a published event
