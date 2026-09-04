## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## ADDED Requirements

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

### Requirement: Apply to a lottery phase

The system SHALL allow an authenticated fan to submit a **`TicketApplication`**
for **1..N tickets** where **N ≤ `max_tickets_per_application`**, only while the
application window is **open**. The application SHALL capture **本人確認**
(applicant name + contact) bound to the account, and SHALL **authorize (hold) the
ticket amount** on the fan's card via a Stripe manual-capture payment
(`capture_method=manual`, 3DS completed once at application). The card MUST be a
**JPY** card of an accepted brand (Visa/Mastercard/JCB/Diners/Discover);
**American Express and non-JPY cards SHALL be rejected** (their authorization
cannot be held for the window). **No money is captured at application** — only
authorized.

#### Scenario: Fan applies within the window

- **WHEN** an authenticated fan applies for N ≤ max tickets while the window is open, provides 本人確認, and completes the card authorization (3DS once)
- **THEN** a TicketApplication is recorded with the payment authorization held and no money captured

#### Scenario: Application outside the window is rejected

- **WHEN** a fan attempts to apply before the phase opens or at/after it closes
- **THEN** the system rejects the application

#### Scenario: Requested count over the max is rejected

- **WHEN** a fan requests more than `max_tickets_per_application` tickets
- **THEN** the system rejects the application

#### Scenario: Unsupported card is rejected

- **WHEN** a fan attempts to apply with an American Express card or a non-JPY card
- **THEN** the system rejects the application (only JPY Visa/Mastercard/JCB/Diners/Discover are accepted, so the authorization can be held until the draw)

#### Scenario: No capture at application

- **WHEN** the card is authorized at application
- **THEN** the ticket amount is only held (authorized), not captured, so a losing fan is never charged

### Requirement: One application per account per phase

The system SHALL allow **at most one** active `TicketApplication` per account per
lottery phase (anti-scalp). A fan MAY **withdraw** their application **before the
draw**, which **releases (cancels) the authorization**; after withdrawal they may
re-apply while the window is still open. There is **no post-draw winner decline**
(the card is captured at the draw with no intervening step); once tickets are
**issued** the application is no longer withdrawable via ④ (the cannot-attend path
is then ⑦ official resale).

#### Scenario: Second application is rejected

- **WHEN** a fan who already has an active application for the phase applies again
- **THEN** the system rejects the second application

#### Scenario: Withdraw before the draw releases the hold

- **WHEN** a fan withdraws their application before the draw
- **THEN** the application is removed from the draw, its authorization is released, and the fan may re-apply while the window is open

#### Scenario: Issued ticket is not withdrawable in ④

- **WHEN** a fan whose tickets are already issued wants to give them up
- **THEN** ④ does not withdraw them (the sanctioned path is ⑦ official resale)

### Requirement: Automatic draw against fixed capacity

The system SHALL run an **automatic draw** when the application window **closes**,
never before. The draw SHALL order applications **uniformly at random**, then
admit each application **whose ticket count fits the remaining capacity**,
allocating **whole applications** (all-or-nothing — a winning application wins
**all** its requested tickets so companion groups stay intact); applications that
do not fit are placed on the waitlist **in that same random order** and the draw
**continues** so smaller later applications can still fill capacity. The draw
MUST NOT oversell capacity. The draw SHALL produce **winners** and a **persisted
ordered waitlist of the remaining (losing) applications** in the random draw
order.

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

### Requirement: Capture winners and release losers at the draw

At the draw, the system SHALL **capture** the authorization of each **winning**
application (this is the charge) and **release/cancel** the authorization of each
**losing** application. A captured winning application SHALL be handed off to
purchase/issuance (⑤) to create the **Order** and issue the **Tickets**. ④ SHALL
NOT create the Order or issue Tickets itself. If a winner's capture fails (an
edge case — e.g. the card was closed between application and the draw), that
application's seat SHALL be left **unfilled** and the failure recorded for manual
follow-up; the MVP SHALL NOT automatically promote a waitlisted application.

#### Scenario: Winner's hold is captured and handed off

- **WHEN** an application wins the draw
- **THEN** its authorization is captured and the captured payment is handed off to purchase/issuance (⑤) to create the Order and issue the Tickets

#### Scenario: Loser's hold is released

- **WHEN** an application loses the draw
- **THEN** its authorization is released (cancelled) so the fan is never charged

#### Scenario: Capture failure leaves the seat unfilled

- **WHEN** a winning application's capture fails at the draw
- **THEN** the seat is left unfilled and the failure is recorded for manual follow-up (no automatic 繰上げ occurs)

### Requirement: Application results

The system SHALL let each applicant see their **result** (won / lost /
withdrawn) after the draw.

#### Scenario: Applicant sees their result

- **WHEN** the draw has completed
- **THEN** each applicant can see whether they won or lost

### Requirement: Persisted loser waitlist for resale

The draw SHALL persist the ordered list of **losing applications** in random draw
order as the demand pool consumed by ⑦ `official-resale` (and any future 二次抽選).
Each losing application maps to **one demand candidate (that account)** in draw
order. The MVP ④ SHALL NOT itself promote from this waitlist (no automatic 繰上げ);
it only persists the ordering for downstream consumers.

#### Scenario: Losing applications are the resale demand pool

- **WHEN** the draw completes with losing applications
- **THEN** they are persisted as an ordered waitlist (random draw order), each account as one demand candidate, available to ⑦ official-resale

### Requirement: 本人確認 binding carried to issuance

The captured **本人確認** (applicant name + contact) SHALL be bound to the
account and carried through to ticket issuance so the issued ticket can be a
**covered ticket (特定興行入場券)**.

#### Scenario: Identity is available at issuance

- **WHEN** a winning application is handed off for issuance
- **THEN** its 本人確認 (name + contact) is available to bind to the issued ticket
