# Issue From Captured Win

## Purpose

This capability turns a **captured** lottery win into an Order and issued tickets:
④ **authorizes (holds) the card at application and captures the winner's
authorization at the draw**; ⑤ takes that **captured winning payment** and records
an Order + issues Web2 account-bound tickets — under the 収納代行 scheme with the
Organizer as seller-of-record. It is the primary Order + issuance pipeline for the
ticketing MVP.

## Requirements

### Requirement: Issue from ④'s captured winning payment

The charge is performed by **④** (a Stripe **manual-capture** authorization held at
application and **captured at the draw** for winners, JPY card only). The captured
funds land on the **platform balance** (④'s charge is a plain platform charge, so it
already holds funds under the 収納代行 scheme); the post-event settlement of the
Organizer's net share is owned by **`ticket-settlement-and-payout`** (see the
delegation requirement below). **④ owns the PaymentIntent lifecycle and its provider
webhooks (authorize / capture / cancel)**;
on a successful capture ④ marks the application **Won-captured**. **⑤ is triggered
by ④'s confirmed-captured signal (the Won-captured application), NOT by a
⑤-owned capture webhook** (in the MVP the handoff is ④'s Won-captured record, not
an event). On that signal ⑤ SHALL create the **Order** referencing ④'s captured
PaymentIntent and proceed to issuance. ⑤ SHALL **NOT** perform a separate
off-session charge; there is **no ⑤-side payment deadline, off-session charge,
re-auth, or 繰上げ** — the hold-and-capture model removes them (④ releases losers'
holds; a capture that never succeeds leaves the seat unfilled for ④'s manual
follow-up).

#### Scenario: Order created from the captured winning payment

- **WHEN** ④ marks a winning application Won-captured (its held authorization captured at the draw)
- **THEN** ⑤ creates an Order referencing that captured PaymentIntent and proceeds to issuance

#### Scenario: ⑤ performs no separate charge and does not own the capture webhook

- **WHEN** a winner is being processed
- **THEN** ⑤ does not run an off-session charge / SetupIntent / payment-deadline / 繰上げ flow, and does not depend on a ⑤-owned capture webhook — the charge, capture, and its webhooks are ④'s; ⑤ keys on the Won-captured signal

#### Scenario: No Won-captured, no Order

- **WHEN** an application is not Won-captured by ④ (lost, or its capture never succeeded)
- **THEN** ⑤ creates no Order and issues no ticket (no ⑤-side retry/繰上げ)

### Requirement: Idempotent issuance

**Capture** and its provider webhooks belong to ④; **refund/dispute** provider
webhooks and their idempotency belong to **`ticket-settlement-and-payout`** (which
makes the refund calls). ⑤ SHALL make **issuance idempotent**: replaying the
Won-captured signal (or retrying issuance) MUST NOT double-issue tickets or
double-create an Order for the same application.

#### Scenario: Replayed captured-win signal issues exactly once

- **WHEN** ④'s Won-captured signal for an application is observed/retried more than once
- **THEN** the Order is created once and tickets are issued exactly once
