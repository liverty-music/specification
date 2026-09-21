# Lottery Application

## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## Requirements

### Requirement: 本人確認 binding carried to issuance

The captured **本人確認** (applicant name + contact) SHALL be bound to the
account and carried through to ticket issuance so the issued ticket can be a
**covered ticket (特定興行入場券)**.

#### Scenario: Identity is available at issuance

- **WHEN** a winning application is handed off for issuance
- **THEN** its 本人確認 (name + contact) is available to bind to the issued ticket
