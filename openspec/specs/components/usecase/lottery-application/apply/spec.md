# Apply

## Purpose

The lottery-application capability lets an Organizer sell a published event's
tickets by lottery: fans apply within a window with their card **authorized (held)
at application**, a fair draw runs against a fixed capacity after applications
close, and at the draw each **winner's hold is captured** while each **loser's
hold is released**. It is the MVP sales method — it removes real-time oversell
from the MVP and matches the JP norm (held at apply, charged on win, released on
loss) for high-demand concerts.

## Requirements

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
