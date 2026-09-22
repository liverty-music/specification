# Run Draw

## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## Requirements

### Requirement: Automatic draw, capture, and release against fixed capacity

The system SHALL run an **automatic draw** when the application window **closes**, never before. The draw SHALL order applications **uniformly at random**, then admit each application **whose ticket count fits the remaining capacity**, allocating **whole applications** (all-or-nothing — a winning application wins **all** its requested tickets so companion groups stay intact); applications that do not fit are placed on the waitlist **in that same random order** and the draw **continues** so smaller later applications can still fill capacity. The draw MUST NOT oversell capacity. The draw SHALL produce **winners** and a **persisted ordered waitlist of the remaining (losing) applications** in the random draw order. At the draw, the system SHALL **capture** the authorization of each **winning** application (this is the charge) and **release/cancel** the authorization of each **losing** application. A captured winning application SHALL be handed off to purchase/issuance to create the Order and issue the Tickets; the draw process SHALL NOT create the Order or issue Tickets itself. If a winner's capture fails (an edge case — e.g. the card was closed between application and the draw), that application's seat SHALL be left **unfilled** and the failure recorded for manual follow-up; the MVP SHALL NOT automatically promote a waitlisted application.

#### Scenario: Draw fills capacity without oversell

- **WHEN** the window closes with applications totaling more tickets than capacity
- **THEN** applications are taken in random order, each is admitted if it fits the remaining capacity (others waitlisted and the draw continues), and the total won tickets never exceed capacity

#### Scenario: Companion group is all-or-nothing

- **WHEN** an application for N tickets is selected
- **THEN** it wins all N tickets (never a partial subset)

#### Scenario: Losers are recorded in a stable order

- **WHEN** the draw completes
- **THEN** the non-winning applications are persisted as an ordered waitlist in draw order

#### Scenario: Draw does not run before close

- **WHEN** the window has not yet closed
- **THEN** no draw runs and no results are available

#### Scenario: Demand at or below capacity

- **WHEN** the window closes with total requested tickets ≤ capacity (including zero applications)
- **THEN** every application wins and the waitlist is empty (no losers)

#### Scenario: Winner's hold is captured and handed off

- **WHEN** an application wins the draw
- **THEN** its authorization is captured and the captured payment is handed off to purchase/issuance (⑤) to create the Order and issue the Tickets

#### Scenario: Loser's hold is released

- **WHEN** an application loses the draw
- **THEN** its authorization is released (cancelled) so the fan is never charged

#### Scenario: Capture failure leaves the seat unfilled

- **WHEN** a winning application's capture fails at the draw
- **THEN** the seat is left unfilled and the failure is recorded for manual follow-up (no automatic 繰上げ occurs)

### Requirement: Persisted loser waitlist for resale

The draw SHALL persist the ordered list of **losing applications** in random draw
order as the demand pool consumed by ⑦ `official-resale` (and any future 二次抽選).
Each losing application maps to **one demand candidate (that account)** in draw
order. The MVP ④ SHALL NOT itself promote from this waitlist (no automatic 繰上げ);
it only persists the ordering for downstream consumers.

#### Scenario: Losing applications are the resale demand pool

- **WHEN** the draw completes with losing applications
- **THEN** they are persisted as an ordered waitlist (random draw order), each account as one demand candidate, available to ⑦ official-resale
