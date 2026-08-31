## Purpose

Official, face-value resale lets a fan who can no longer attend hand their
issued ticket back for a sanctioned face-value re-sale, so no seat is wasted and
no scalping or person-to-person payment ever occurs. It is the anti-scalp,
legally favored alternative to ad-hoc refunds and private transfers.

## ADDED Requirements

### Requirement: List a ticket for resale

The system SHALL allow the current **owner** of a ticket to list it for official
resale when the ticket is **PAID and unused**, its event is in the **future**,
resale is **enabled** for that event, and the **resale deadline has not passed**.
The listing price SHALL be **fixed to the ticket's face value** — defined as the
**ticket price (券面代金) only, excluding the original purchase-side booking/service
fee** — the seller MUST NOT be able to set any other price. A ticket that is
already listed, used, refunded, or belongs to a past/cancelled event MUST NOT be
listable.

#### Scenario: Owner lists an eligible ticket

- **WHEN** the owner of a PAID, unused ticket for a future resale-enabled event lists it before the deadline
- **THEN** a resale listing is created in state LISTED at the ticket's original face value, and the ticket becomes visible in the resale demand-matching pool

#### Scenario: Price is locked to face value

- **WHEN** a listing is created
- **THEN** its price equals the ticket's original purchase price and cannot be set above or below it

#### Scenario: Ineligible ticket is rejected

- **WHEN** the owner attempts to list a ticket that is used, already listed, refunded, or for a past or cancelled event
- **THEN** the system rejects the listing with a precondition failure and no listing is created

### Requirement: Resale deadline

The system SHALL stop accepting new listings and stop matching at a **resale
deadline of one hour before the event start time (`start_time − 1h`)**. An
Organizer MAY configure an **earlier** cutoff for their event but MUST NOT set a
later one.

#### Scenario: Listing after the deadline is rejected

- **WHEN** the owner attempts to list a ticket at or after `start_time − 1h` (or the organizer's earlier cutoff)
- **THEN** the system rejects the listing because the resale window has closed

#### Scenario: Organizer sets an earlier cutoff

- **WHEN** an Organizer configures a resale cutoff earlier than `start_time − 1h`
- **THEN** listing and matching stop at that earlier time for that event

### Requirement: Ticket sales require complete event info

The system SHALL only accept ticket sales — primary and resale — for an event
whose **mandatory event information, including `start_time`, is set**. Because the
resale deadline is derived as `start_time − 1h`, an event missing `start_time`
MUST NOT be sellable/resellable (the deadline is otherwise uncomputable).

#### Scenario: Event missing start_time is not sellable

- **WHEN** an event is published without its mandatory info (e.g. no `start_time`)
- **THEN** the system does not accept ticket sales or resale listings for it until the required info is set

### Requirement: Withdraw a listing

The system SHALL allow the seller to **withdraw** their listing **only while it is
in `LISTED` state** (not while an offer is in flight or after a match), returning
the ticket to normal OWNED state with no fee charged. While a seat is `OFFERED` to
a candidate the listing is locked and MUST NOT be withdrawable — this resolves the
withdraw-vs-purchase race in favor of the in-flight offer.

#### Scenario: Seller withdraws while LISTED

- **WHEN** the seller withdraws a listing that is in LISTED state with no offer in flight
- **THEN** the listing moves to WITHDRAWN, the ticket returns to OWNED, and no fee is charged

#### Scenario: Withdrawal is rejected while an offer is in flight or after match

- **WHEN** the seller attempts to withdraw a listing that is OFFERED to a candidate or already SOLD
- **THEN** the system rejects the withdrawal (the offer/match takes precedence)

### Requirement: Resale is enabled by default with structural exclusions only

The system SHALL treat official resale as **enabled by default on every standard
paid event** (consent obtained as a blanket, standing grant in the vetted
Organizer's platform agreement). It SHALL provide **no organizer self-serve
off-switch**. A ticket SHALL be **non-resellable only** when an automatic
**structural exclusion** applies — the ticket is **free (¥0)**, a **comp/invite**,
**bundled with physical goods**, or a **name-locked special ticket** (a ticket
type flagged as non-transferable by design — e.g. an FC-restricted or
named-holder-only ticket — which is distinct from the ordinary 本人確認 binding
that every covered ticket, including reissued resale tickets, carries) — or when an
**administrator** grants a documented exception for the event. These exclusion
flags are ticket-type metadata defined by ⑤/⑥ (see design.md dependency).

#### Scenario: Standard paid event is resale-enabled without organizer action

- **WHEN** a vetted Organizer publishes a standard paid event
- **THEN** official resale is enabled for that event by default with no per-event opt-in step

#### Scenario: Structurally excluded ticket cannot be listed

- **WHEN** the owner attempts to list a free, comp, goods-bundled, or name-locked ticket
- **THEN** the system rejects the listing because the ticket is structurally excluded from resale

#### Scenario: Administrator excludes an event by exception

- **WHEN** an administrator records a documented resale exception for a specific event
- **THEN** listing is disabled for that event, LISTED listings are withdrawn, and any in-flight OFFERED offer is voided with no charge (admin action overrides the OFFERED lock, which only blocks the *seller*'s own withdrawal); already-SOLD resales are unaffected

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

### Requirement: Seller refund triggered on resale completion

The system SHALL refund the seller **their own original payment minus the resale
fee**, **triggered at the atomic match** (the resale completing), **NOT held to
the event**. The net settlement to the seller SHALL carry a **hold-back reserve —
a fixed window measured from the match** (a dispute buffer; ~days to ~3 weeks, the
exact length a tunable operational parameter) — after which it releases; it MUST
NOT be tied to the event occurring. If the seller's original
payment method can no longer be reversed at settlement time (e.g. an expired card),
the system SHALL fall back to an alternative payout (e.g. bank transfer).

#### Scenario: Refund triggered when the resale completes

- **WHEN** a resale match completes
- **THEN** the seller's refund (original payment minus the resale fee) is triggered, subject to a short hold-back reserve, without waiting for the event

#### Scenario: Chargeback handled via hold-back, not event-gating

- **WHEN** a buyer charges back a resold seat
- **THEN** the platform draws on the hold-back reserve and represents the dispute with the delivered-ticket / entry evidence, clawing back via reversal if needed

#### Scenario: Refund falls back when the card cannot be reversed

- **WHEN** the seller's original card is expired or closed at settlement time
- **THEN** the system pays the seller via an alternative payout method instead of a card reversal

### Requirement: Resale fee

The system SHALL charge the **seller** a **single resale fee as a percentage of
face value** (default ~10%, business-configurable), and SHALL charge it **only on
a successful resale**. If a listing does not sell, the system MUST NOT charge any
fee. The fee SHALL be defined in the terms as **consideration for a service
rendered (役務提供の対価** — matching / payment / 本人確認), not a cancellation
penalty (違約金). Fee computation SHALL apply a **defined rounding rule** and, when
the seller's refundable original amount is less than the computed fee, SHALL
**clamp the fee to the refundable amount** (never producing a negative payout). The
fee and per-Organizer 事業者情報 SHALL be disclosed on the confirmation screen
(特定商取引法に基づく表記).

#### Scenario: Fee charged only on success

- **WHEN** a listing sells
- **THEN** the seller's refund is reduced by the resale fee and the fee terms were disclosed before listing

#### Scenario: No fee when unsold

- **WHEN** a listing does not sell by the deadline
- **THEN** no resale fee is charged

#### Scenario: Fee is clamped to the refundable amount

- **WHEN** the computed fee would exceed the seller's refundable original amount
- **THEN** the fee is clamped so the seller payout is never negative

### Requirement: Buyer return policy on the final confirmation screen

The system SHALL display a **返品特約 (no-return / no-cancellation clause)** to the
resale **buyer** on the **final order-confirmation screen** (the screen
immediately before the confirm-purchase action), clearly and legibly — **not only
as a link to the terms**. This is **required separately from the fee disclosure**
and satisfies 特商法 §12-6 so the default 8-day 通信販売 return right (§15-3) does
not apply. Event-cancellation refunds are a **separate** matter governed by the
ticket's cancellation policy and MUST NOT contradict this clause.

#### Scenario: Return policy shown before purchase confirmation

- **WHEN** a buyer reaches the final confirmation screen for a resale purchase
- **THEN** a clear "purchase is non-returnable / non-cancellable" clause is displayed on that screen, distinct from the fee disclosure

### Requirement: Covered-ticket re-bind on reissue

On reissue to the buyer the system SHALL capture the **new holder's 本人確認**
(name + contact) and SHALL keep the reissued ticket a **特定興行入場券**: its face
states that resale without organizer consent is prohibited, specifies
date/venue + seat-or-eligible-person, and records the holder's identity. The
voided original MUST NOT remain usable for entry.

#### Scenario: Reissued ticket is identity-bound to the buyer

- **WHEN** a new ticket is issued to the resale buyer
- **THEN** it carries the buyer's 本人確認 and the covered-ticket face conditions, and the seller's voided ticket cannot enter

### Requirement: Resold companion seat leaves the same-time-entry group

When a lead resells **one** seat of a same-time-entry (連番) group, that seat SHALL
**leave the group** and be reissued to the anonymous buyer as an independent
entry; the group MUST NOT be forced to admit the stranger. The lead's remaining
seats keep their same-time-entry linkage.

#### Scenario: One companion seat is resold

- **WHEN** the lead of a group resells one of their same-time-entry seats
- **THEN** the resold seat is reissued as an independent entry to the new buyer, and the lead's remaining seats keep their grouping

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

### Requirement: Unsold listing returns to the holder

The system SHALL return an **unsold** ticket to its holder at the deadline so the
holder may still attend, charging **no fee**. A **scheduled sweep** (not a lazy
on-access check) SHALL transition unsold `LISTED` listings to `EXPIRED` at the
deadline so no listing is left dangling. Resale SHALL be presented as **not
guaranteed**, disclosed **before** listing.

#### Scenario: Unsold ticket is returned

- **WHEN** the resale deadline passes with the listing unmatched
- **THEN** the scheduled sweep moves the listing to EXPIRED, the ticket returns to the holder as valid for entry, and no fee is charged

### Requirement: Event cancellation or postponement while listed

When an event is **cancelled** while a ticket is in `LISTED` or `OFFERED` state
(fresh-sale leg not yet completed), the system SHALL cancel the listing/offer and
route the ticket to the **normal cancellation-refund path** — the resale
fresh-sale leg MUST NOT execute. When an event is **postponed**, existing `LISTED`
listings SHALL remain valid and any **in-flight `OFFERED` offer SHALL continue**
against the **recomputed** resale **deadline** (new `start_time − 1h`), and any
already-completed resale SHALL be unaffected (the reissued ticket stays valid for
the new date). Because the seller refund is keyed
on resale completion (not the event), postponement does not change settled refunds.

#### Scenario: Cancellation supersedes a live listing

- **WHEN** an event is cancelled while a ticket is in LISTED or OFFERED state
- **THEN** the listing/offer is cancelled and the holder receives the standard cancellation refund, not a resale outcome

#### Scenario: Postponement recomputes the deadline and preserves settled resales

- **WHEN** an event is postponed
- **THEN** open listings stay valid with the deadline recomputed to the new start time, and any completed resale and its settled refund are unaffected

### Requirement: Anonymity and no person-to-person contact

The system SHALL keep sellers and buyers **anonymous to each other**: they MUST
NOT exchange personal information and money MUST NOT move person-to-person. All
matching happens through the platform pool.

#### Scenario: No personal information is exchanged

- **WHEN** a resale match completes
- **THEN** neither party learns the other's identity or contact details, and no direct payment occurred between them
