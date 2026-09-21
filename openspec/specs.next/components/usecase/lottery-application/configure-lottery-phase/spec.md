# Configure Lottery Phase

## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## Requirements

### Requirement: Configure a lottery sales phase

The system SHALL allow an Organizer to add a **lottery sales phase** to a
**published** event of theirs (an Event whose concert/Series is `PUBLISHED` per
organizer-event-authoring — the phase is unavailable while the concert is DRAFT),
specifying an **application window** (open time and close time) whose **duration
is between 1 and 14 days inclusive** (the organizer console SHALL default the
duration to **10 days**), a **capacity in tickets** (a positive integer the
**Organizer sets**, sized by the Organizer to the venue — ④ does not read a
venue-capacity field, none exists upstream), a **`max_tickets_per_application`**
(a positive integer ≤ capacity), and a **per-ticket price in JPY** (a positive
whole number of yen). Capacity SHALL be accounted in **tickets**, not
applications. The price is required because ④ authorizes **price × requested
ticket count** on the fan's card at application.

#### Scenario: Organizer configures a lottery phase

- **WHEN** an Organizer adds a lottery phase to a published event with a valid window (duration 1–14 days), ticket capacity, max-tickets-per-application, and a positive JPY ticket price
- **THEN** the phase is created and fans can apply once it opens

#### Scenario: Phase on an unpublished concert is rejected

- **WHEN** an Organizer tries to add a lottery phase to an event whose concert/Series is still DRAFT
- **THEN** the system rejects it (the concert must be published first)

#### Scenario: Invalid phase configuration is rejected

- **WHEN** the close time is not after the open time, or the window duration is shorter than 1 day or longer than 14 days, or capacity / max-tickets-per-application / ticket price is not a positive integer, or max-tickets-per-application exceeds capacity
- **THEN** the system rejects the configuration
