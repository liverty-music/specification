## MODIFIED Requirements

### Requirement: Capture winners and release losers at the draw

At the draw, the system SHALL **capture** the authorization of each **winning**
application (this is the charge) and **release/cancel** the authorization of each
**losing** application. The winner's capture SHALL be a **platform-held separate
charge** — the captured funds land on the **platform** balance (Stripe **separate
charges & transfers**, with **no** `transfer_data[destination]` / `on_behalf_of`
at capture), so the platform custodies the money until the event under the 収納代行
scheme; the platform takes its fee as the **retained** portion and the Organizer's
net share is settled by a **post-event `Transfer`** (see ⑤'s payout leg), **not**
by settling to the Organizer at capture. A captured winning application SHALL be
handed off to purchase/issuance (⑤) to create the **Order** and issue the
**Tickets**. ④ SHALL NOT create the Order or issue Tickets itself. If a winner's
capture fails (an edge case — e.g. the card was closed between application and the
draw), that application's seat SHALL be left **unfilled** and the failure recorded
for manual follow-up; the MVP SHALL NOT automatically promote a waitlisted
application.

#### Scenario: Winner's hold is captured and handed off

- **WHEN** an application wins the draw
- **THEN** its authorization is captured and the captured payment is handed off to purchase/issuance (⑤) to create the Order and issue the Tickets

#### Scenario: Captured funds are held on the platform balance

- **WHEN** a winning application's authorization is captured at the draw
- **THEN** the funds land on the platform balance (a separate charge, no destination/on_behalf_of at capture), not settled to the Organizer — so the platform holds them until the post-event Transfer

#### Scenario: Loser's hold is released

- **WHEN** an application loses the draw
- **THEN** its authorization is released (cancelled) so the fan is never charged

#### Scenario: Capture failure leaves the seat unfilled

- **WHEN** a winning application's capture fails at the draw
- **THEN** the seat is left unfilled and the failure is recorded for manual follow-up (no automatic 繰上げ occurs)
