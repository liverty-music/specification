# Ticket

## Purpose

This capability turns a **captured** lottery win into an Order and issued tickets:
④ **authorizes (holds) the card at application and captures the winner's
authorization at the draw**; ⑤ takes that **captured winning payment** and records
an Order + issues Web2 account-bound tickets — under the 収納代行 scheme with the
Organizer as seller-of-record. It is the primary Order + issuance pipeline for the
ticketing MVP.

## Requirements

### Requirement: Issue account-bound covered tickets on the captured win

On ④'s **Won-captured** signal the system SHALL issue **N account-bound Tickets**.
Each SHALL be a **covered ticket (特定興行入場券)** carrying **all three** legal
conditions: (i) the face states **resale without organizer consent is prohibited**,
(ii) the face specifies **date/venue + eligible-person** (the lottery is a common
pool with **no seat map** — the eligible-person is the bound holder, seat is
general-admission/none), and (iii) the **本人確認** is captured and noted on the
face, bound to the buyer's account. **本人確認 source depends on the phase's
verification requirement:** where the phase **required identity verification**
(identity-ekyc), the **verified identity is authoritative** and the bound name
MUST match the verified 本人確認 (no conflicting self-declared name); otherwise ④'s
**self-declared name + contact** is bound. Tickets MUST NOT be issued on a
client-side confirmation alone (issuance keys on ④'s captured-win signal).

#### Scenario: Tickets issued on the captured win

- **WHEN** ④ marks a winning application Won-captured
- **THEN** N account-bound covered tickets are issued to the buyer

#### Scenario: Issued ticket carries all three covered-ticket conditions

- **WHEN** a ticket is issued
- **THEN** its face states resale-without-consent is prohibited, specifies date/venue + eligible-person, and records the holder's 本人確認 (so it qualifies as a 特定興行入場券)

#### Scenario: Verified identity binds the covered ticket where required

- **WHEN** the phase required identity verification and a verified person's win is issued
- **THEN** the covered-ticket 本人確認 is the verified identity (a conflicting self-declared name is not bound)

#### Scenario: No issuance without the captured-win signal

- **WHEN** no ④ Won-captured signal exists for an application
- **THEN** no ticket is issued
