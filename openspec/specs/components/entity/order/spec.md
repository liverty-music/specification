# Order

## Purpose

This capability turns a **captured** lottery win into an Order and issued tickets:
④ **authorizes (holds) the card at application and captures the winner's
authorization at the draw**; ⑤ takes that **captured winning payment** and records
an Order + issues Web2 account-bound tickets — under the 収納代行 scheme with the
Organizer as seller-of-record. It is the primary Order + issuance pipeline for the
ticketing MVP.

## Requirements

### Requirement: Order record

The system SHALL create an **`Order`** for each purchase that is **provider- and
method-agnostic**: it stores opaque provider references (e.g. `pi_`/`pm_`), its
own `status` (**`paid`** on creation — the Order is created from an already-captured
payment — then `refunded`, or `failed` for the capture-succeeded-but-issuance-
refunded edge), `amount`+`currency`, `paid_at` (= the capture time), and optional
display facets (card brand/last4) — **never** PAN, CVC, or expiry. There is **no
`pending` Order** (the pre-capture authorize/hold state lives on ④'s
`TicketApplication`, not on ⑤'s Order). One Order SHALL cover the **N tickets** of
the winning application.

#### Scenario: Order is created already paid, referencing the captured payment

- **WHEN** an Order is created from ④'s captured winning payment
- **THEN** its status is `paid` with `paid_at` = the capture time, it stores only opaque provider token references, and never stores PAN/CVC/expiry

#### Scenario: One Order spans the companion group

- **WHEN** a winning application for N tickets is captured
- **THEN** a single Order covers all N tickets
