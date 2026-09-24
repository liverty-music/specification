## Purpose

Matches a listed ticket to a buyer drawn from the public resale queue, giving lottery-losers priority over the general public, and settles the buyer's face-value payment while voiding and reissuing the ticket atomically so money never passes directly between seller and buyer.

## ADDED Requirements

### Requirement: Public resale marketplace with lottery-loser priority

The system SHALL expose resale inventory as a **publicly visible, publicly
joinable marketplace** — any buyer can discover available resale seats and join
the demand queue (not hidden behind a pre-registered waitlist). Matching SHALL be
**priority-ordered, NOT first-come**: **lottery-losers first in draw order, then
the general public in join order**. "Draw order" is the stable loser ordering
persisted by ④ `lottery-application`; **if ④ does not persist one, the fallback is
lottery-application-timestamp order**. A listed seat SHALL be offered
**sequentially** down this ordered queue via a **time-limited offer** (state
`OFFERED`); on expiry — or if the candidate **explicitly declines**, or **becomes
ineligible while OFFERED** (e.g. they separately win the event's lottery or buy a
primary ticket, tripping the per-person limit) — the offer SHALL be voided and
pass to the next candidate (an ineligible candidate MUST NOT be allowed to
complete). The system **MUST NOT start an offer whose window would extend past the
resale deadline**. If the offer reaches the end of the queue with no buyer and the
deadline has not passed, the listing SHALL **return to `LISTED` (it MUST NOT go
dead)** and be re-offered as new candidates join. Buyers SHALL NOT be able to
designate a particular seller (the pool is anonymous).

#### Scenario: Inventory is publicly discoverable

- **WHEN** any eligible buyer views an event with resale seats available
- **THEN** they can see resale availability and join the demand queue without prior registration

#### Scenario: Loser is offered ahead of the general public

- **WHEN** a seat becomes available and the queue contains lottery-losers and general-public joiners
- **THEN** the seat is offered to the earliest-drawn lottery-loser before any general-public joiner

#### Scenario: Timed offer expires and passes on

- **WHEN** a candidate does not complete the face-value purchase within the offer window
- **THEN** the offer expires and is extended to the next candidate in priority order

#### Scenario: Candidate declines or becomes ineligible mid-offer

- **WHEN** an OFFERED candidate explicitly declines, or becomes ineligible while the offer is open (e.g. wins the event's lottery or buys a primary ticket)
- **THEN** the offer is voided immediately and passes to the next candidate, and the now-ineligible candidate is not allowed to complete the purchase

#### Scenario: Offer window is not started past the deadline

- **WHEN** the remaining time to the resale deadline is shorter than the offer window
- **THEN** the system does not start a new offer that would extend past the deadline

#### Scenario: Queue exhausted before deadline keeps the listing alive

- **WHEN** the offer reaches the end of the current queue with no buyer and the deadline has not passed
- **THEN** the listing returns to LISTED and is re-offered when new candidates join (the seat does not silently go dead)

#### Scenario: Buyer cannot pick a seller

- **WHEN** a buyer joins the demand queue
- **THEN** they receive an anonymous match and cannot select or contact a specific seller

### Requirement: Two-leg money model at match time

On a successful match the system SHALL, **in one atomic transaction**: (1) settle
the **buyer's fresh face-value payment** to the Organizer/platform (収納代行,
payee = Organizer, same scheme as the primary sale), (2) **void** the seller's
original ticket so its rotating QR can no longer enter, and (3) **issue a new
ticket** to the buyer. The buyer SHALL pay **exactly face value** (券面代金) with no
buyer-side markup or fee. **Money MUST NEVER move directly from the buyer to the
seller** — the two legs are decoupled: the seller is only ever **refunded their
own original payment**, never paid as the transferee of the buyer's funds. (Legal
detail — including the 資金決済法 2条の2第2号 escrow-exclusion backstop if the seller
is nonetheless viewed as a payee — lives in `docs/resale-design.md`, not this spec.)

#### Scenario: Match settles buyer and voids seller atomically

- **WHEN** a buyer completes the offered face-value purchase
- **THEN** the buyer's payment settles, the seller's original ticket is voided, and a new ticket is issued to the buyer — all or nothing

#### Scenario: Buyer pays exactly face value

- **WHEN** a buyer is charged for a resold seat
- **THEN** the amount equals the ticket's face value with no buyer-side resale markup

#### Scenario: Failed buyer payment leaves the seat listed

- **WHEN** the buyer's payment fails during a match
- **THEN** no ticket is voided or issued and the listing remains LISTED for the next candidate

### Requirement: Covered-ticket re-bind on reissue

On reissue to the buyer the system SHALL capture the **new holder's 本人確認**
(name + contact) and SHALL keep the reissued ticket a **特定興行入場券**: its face
states that resale without organizer consent is prohibited, specifies
date/venue + seat-or-eligible-person, and records the holder's identity. The
voided original MUST NOT remain usable for entry.

#### Scenario: Reissued ticket is identity-bound to the buyer

- **WHEN** a new ticket is issued to the resale buyer
- **THEN** it carries the buyer's 本人確認 and the covered-ticket face conditions, and the seller's voided ticket cannot enter

### Requirement: No double-seat or double-charge across lottery and resale

The system SHALL prevent a user from holding or being charged for more than the
event's per-person ticket limit across primary + resale. Accepting a resale offer
SHALL **remove the candidate from that event's unresolved lottery pool(s)** — an
"unresolved" pool being any draw for that event that has not yet been finalized —
and a user who **already holds a ticket for the event** SHALL be **excluded from
that event's resale demand queue**.

#### Scenario: Accepting a resale seat removes the user from pending draws

- **WHEN** a lottery-loser accepts a resale offer for an event that still has an unresolved draw
- **THEN** the user is removed from that event's pending draw so they cannot also win and be charged twice

#### Scenario: Existing holder is excluded from the demand queue

- **WHEN** a user who already holds a ticket for the event tries to join that event's resale demand queue
- **THEN** the system excludes them (respecting the per-person limit)
