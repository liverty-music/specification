## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window, a fair draw runs against a fixed
capacity after applications close, and winners gain the right to be charged. It
is the MVP sales method — it removes real-time oversell from the MVP and matches
the JP norm for high-demand concerts.

## ADDED Requirements

### Requirement: Configure a lottery sales phase

The system SHALL allow an Organizer to add a **lottery sales phase** to a
**published** event of theirs (an Event whose concert/Series is `PUBLISHED` per
organizer-event-authoring — the phase is unavailable while the concert is DRAFT),
specifying an **application window** (open time and close time, open < close), a
**capacity in tickets** (a positive integer the **Organizer sets** for the phase,
sized by the Organizer to the venue — ④ does not read a venue-capacity field, none
exists upstream), a **`max_tickets_per_application`** (a positive integer ≤
capacity), and a **`payment_deadline` policy** for winners (e.g. a fixed duration
after the draw, or an absolute time; see "Winner payment deadline"). Capacity
SHALL be accounted in **tickets**, not applications.

#### Scenario: Organizer configures a lottery phase

- **WHEN** an Organizer adds a lottery phase to a published event with a valid window, ticket capacity, max-tickets-per-application, and payment-deadline policy
- **THEN** the phase is created and fans can apply once it opens

#### Scenario: Phase on an unpublished concert is rejected

- **WHEN** an Organizer tries to add a lottery phase to an event whose concert/Series is still DRAFT
- **THEN** the system rejects it (the concert must be published first)

#### Scenario: Invalid phase configuration is rejected

- **WHEN** the close time is not after the open time, or capacity / max-tickets-per-application is not a positive integer, or max-tickets-per-application exceeds capacity, or the payment-deadline policy is missing
- **THEN** the system rejects the configuration

### Requirement: Apply to a lottery phase

The system SHALL allow an authenticated fan to submit a **`TicketApplication`**
for **1..N tickets** where **N ≤ `max_tickets_per_application`**, only while the
application window is **open**. The application SHALL capture **本人確認**
(applicant name + contact) bound to the account, and SHALL **save a payment
method via a Stripe `SetupIntent`** (`usage=off_session`, 3DS completed once at
setup, **no authorization hold**) storing only the returned token references. No
charge occurs at application time.

#### Scenario: Fan applies within the window

- **WHEN** an authenticated fan applies for N ≤ max tickets while the window is open, provides 本人確認, and completes the SetupIntent
- **THEN** a TicketApplication is recorded with the saved payment-method reference and no money is charged

#### Scenario: Application outside the window is rejected

- **WHEN** a fan attempts to apply before the phase opens or at/after it closes
- **THEN** the system rejects the application

#### Scenario: Requested count over the max is rejected

- **WHEN** a fan requests more than `max_tickets_per_application` tickets
- **THEN** the system rejects the application

#### Scenario: No authorization hold at application

- **WHEN** the payment method is saved at application
- **THEN** it uses a SetupIntent with no hold on the fan's balance (so prepaid/debit cards work and parallel applications do not tie up credit)

### Requirement: One application per account per phase

The system SHALL allow **at most one** active `TicketApplication` per account per
lottery phase (anti-scalp). A fan MAY **withdraw** their application **before the
draw**; after withdrawal they may re-apply while the window is still open. A
**won** applicant MAY **decline before being charged** (before the off-session
charge succeeds); a decline SHALL be treated like a charge failure — the win is
voided and the next waitlisted application is promoted (繰上げ). Once tickets are
**issued** (charged), the application is no longer withdrawable via ④ (the
cannot-attend path is then ⑦ official resale).

#### Scenario: Second application is rejected

- **WHEN** a fan who already has an active application for the phase applies again
- **THEN** the system rejects the second application

#### Scenario: Withdraw before the draw

- **WHEN** a fan withdraws their application before the draw
- **THEN** the application is removed from the draw and the fan may re-apply while the window is open

#### Scenario: Winner declines before being charged

- **WHEN** a won applicant declines before the off-session charge has succeeded
- **THEN** the win is voided and the next waitlisted application is promoted (繰上げ)

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

### Requirement: Application results

The system SHALL let each applicant see their **result** (won / lost /
promoted / withdrawn) after the draw, and winners SHALL see their **payment
deadline**.

#### Scenario: Applicant sees their result

- **WHEN** the draw has completed
- **THEN** each applicant can see whether they won or lost, and a winner can see their payment deadline

### Requirement: Winning confers the right to be charged

A **won** application SHALL confer the **right to be charged** for its tickets and
SHALL be handed off to purchase/issuance (⑤) for an **off-session charge of the
saved payment method**. ④ SHALL NOT perform the charge itself; it SHALL record
the win, set the **payment deadline** (per the phase's deadline policy), and hand
off. (⑤ owns the charge, Order, and Ticket issuance.)

#### Scenario: Win is handed off for charging

- **WHEN** an application wins
- **THEN** it is marked won with a payment deadline and handed off to the purchase/issuance flow for an off-session charge of the saved payment method

### Requirement: Winner payment deadline (owned by ④)

④ SHALL **own the payment-deadline clock**: it sets each winner's deadline from
the phase policy and **detects lapse**. ⑤ reports each charge attempt's outcome
(**succeeded** / **failed** / **needs re-authentication**); it does **not** own
the deadline. **Before** the deadline, a `failed` or `needs-re-authentication`
outcome SHALL keep the win alive with a **grace window + a re-auth link** so the
winner can fix their card / complete a 3DS step-up (payments-design "winner-
charge-failure flow"). Only when the **deadline lapses without a successful
charge** SHALL ④ void the win.

#### Scenario: Transient failure keeps the win alive until the deadline

- **WHEN** ⑤ reports a charge `failed` or `needs re-authentication` and the deadline has not lapsed
- **THEN** ④ keeps the win and surfaces a re-auth link + grace window; it does not void the win yet

#### Scenario: Deadline lapse without success voids the win

- **WHEN** the payment deadline lapses with no successful charge
- **THEN** ④ voids the win and triggers 繰上げ

### Requirement: Waitlist promotion (繰上げ)

On a **voided win** (deadline lapsed without success, or a pre-charge decline),
the system SHALL **promote the next eligible application on the ordered waitlist**
(繰上げ) in persisted draw order, granting it the same right-to-be-charged and a
**fresh payment deadline**, without oversell. Promotion SHALL **skip** any
application that has been **withdrawn** or is otherwise ineligible, and continue
down the list. A promoted application whose own charge then fails past its
deadline SHALL cascade to the **next** eligible application.

#### Scenario: Next eligible application is promoted

- **WHEN** a win is voided and the waitlist has eligible applications
- **THEN** the next eligible application in draw order is promoted with a fresh deadline, skipping any withdrawn/ineligible ones, without exceeding capacity

#### Scenario: Promotion cascades on repeated failure

- **WHEN** a promoted application also fails past its fresh deadline
- **THEN** the next eligible application is promoted (the cascade continues down the ordered waitlist)

#### Scenario: Promotion stops when no eligible application remains

- **WHEN** no eligible applications remain on the waitlist
- **THEN** the freed capacity is left unfilled (no promotion occurs)

### Requirement: 本人確認 binding carried to issuance

The captured **本人確認** (applicant name + contact) SHALL be bound to the
account and carried through to ticket issuance so the issued ticket can be a
**covered ticket (特定興行入場券)**.

#### Scenario: Identity is available at issuance

- **WHEN** a winning application is handed off for issuance
- **THEN** its 本人確認 (name + contact) is available to bind to the issued ticket
