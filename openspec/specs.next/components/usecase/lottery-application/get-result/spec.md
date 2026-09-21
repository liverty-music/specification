# Get Result

## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## Requirements

### Requirement: Application results

The system SHALL let each applicant see their **result** (won / lost /
withdrawn) after the draw.

#### Scenario: Applicant sees their result

- **WHEN** the draw has completed
- **THEN** each applicant can see whether they won or lost
