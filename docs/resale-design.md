# Resale Design (official-resale)

Durable design for **official, face-value ticket resale** — the sanctioned
"cannot-attend" safety valve. Consolidates the 2025-2026 legal + competitor
research so it is not lost. Companion to [`payments-design.md`](./payments-design.md)
(shares the Stripe Connect / 収納代行 money scheme) and grounded in
[`ticketing-platform-roadmap.md`](./ticketing-platform-roadmap.md)
("Cannot-attend → official face-value resale"). **Not legal advice — the
counsel brief must be confirmed before launch.**

Feeds the future `official-resale` OpenSpec change. **Depends on ④
`lottery-application` (the loser demand pool), ⑤ `ticket-purchase-and-issuance`
(Order/Payment/Ticket + 収納代行 + refunds), and ⑥ `ticket-wallet-and-checkin`
(issue / void / rotating-QR / 本人確認 binding).** Roadmap timing: **leaning
EARLY** — official resale is now a JP market default (post-チケトレ).

## The core model (settled)

Official resale is **NOT a buyer↔buyer transfer**. It is **two decoupled
legs** — a refund of the seller's own purchase + a fresh face-value sale to a
new buyer — so **money never moves from one individual to another**. This is
the universal JP official pattern (ぴあ / ローチケ / e+ / ticket board /
チケトレ) and is what keeps the platform a 収納代行 (payee = the business
Organizer) rather than a 為替取引 / 資金移動業.

```
Resale match (two decoupled legs)

 LEG 1 — seller side (a REFUND of the seller's own money)
   void the seller's original ticket
   → refund the seller their original payment  MINUS a resale fee
   (Stripe Refund on the seller's own PaymentIntent — NOT the buyer's cash)

 LEG 2 — buyer side (a fresh FACE-VALUE sale, payee = Organizer)
   new buyer pays the Organizer/platform at face value (収納代行, same as ⑤)
   → a NEW ticket is issued to the buyer, 本人確認 re-bound to them

 The buyer's payment funds the escrow; the seller only ever gets their own
 money back (primary theory: not a payee at all). Backstop: even if the seller
 is viewed as a payee, the 2条の2第2号 escrow exclusion applies → no 資金移動業.
```

**This two-leg refund model is exactly how incumbents implement it** — tiget
refunds the reselling seller by **reversing their original card charge** (minus a
fixed fee) the moment the resale sells; ticket board 定価トレード / e+ / ぴあ do the
same. So LEG 1 = "refund the seller's own original PaymentIntent" is the
industry-standard construction, not a novel one. As a legal backstop for the
seller (an *individual* payee), the seller leg also fits the 資金決済法 2条の2第2号
**escrow exclusion** (funds received before/with the counter-performance, moved to
the payee **after the counter-performance = the seller handing the ticket to the
buyer**, i.e. void+reissue — NOT the event; see D1).

## Legal must-haves (compliant official resale)

Confirmed against 文化庁 / 警察庁 / 古物営業法 / 消費者庁 (2024-2026):

1. **Keep the ticket a "特定興行入場券" (チケット不正転売禁止法).** Both the
   original and the reissued ticket must carry the 3-condition set: (i) face
   states resale-without-organizer-consent is prohibited, (ii) date/venue +
   seat-or-eligible-person specified, (iii) 本人確認 (name + contact) captured
   and noted on the face. (Same set ④/⑥ already require for the primary sale.)
2. **Face-value only.** Resale price is locked to the original purchase price
   (never above) — above-face is the crime the law targets.
3. **Organizer-consented (blanket, via the platform agreement — D2).** The law
   requires the *organizer's consent* for a resale to be sanctioned, but does
   NOT require that consent be revocable per event. The vetted Organizer grants
   **blanket, standing consent** in the platform agreement at onboarding
   ("official face-value resale is enabled for all my events"), so official
   resale is **mandatory-by-default on every standard paid event** — never an
   "unauthorized" transfer. There is **no organizer self-serve off-switch**; the
   only non-resellable seats are **structural exclusions** (free/¥0, comp/invite,
   goods-bundled, name-locked special tickets) auto-detected by the platform,
   plus rare **admin-approved** exceptions for a documented contractual reason.
4. **Re-bind 本人確認 to the new holder.** On sale, **void/return the original**
   and **issue a new ticket with the new buyer's 本人確認** — preserving the
   covered-ticket status for the new owner (ぴあ/チケプラ practice).
5. **Pure intermediary, no inventory → avoid 古物商許可.** The platform must
   NOT buy-and-hold tickets. A no-inventory, organizer-consigned,
   electronic-ticket resale (void-original + reissue) falls in the
   licence-exempt zone; buying/stocking physical tickets would require a
   金券類 古物商許可. Electronic-only reinforces non-古物 treatment.
6. **特商法 disclosure.** Show the resale fee (a single % of face value — no cap),
   any seller-side transfer fee, and per-Organizer 事業者情報 in the
   特定商取引法に基づく表記 / confirmation screen. (There is **no buyer-side fee** —
   the buyer pays exactly 券面代金; D4.)
7. **返品特約 (return policy) on the buyer's final confirmation screen — a
   requirement DISTINCT from fee disclosure.** A 通信販売 purchase (the buyer's
   fresh face-value sale) carries a **default 8-day statutory return right
   (特商法 §15-3) UNLESS a 返品不可 clause is displayed**. 特商法 §12-6 (令和3年改正,
   in force 2022-06) requires the 撤回・解除に関する事項 (= the return policy) to be
   shown **clearly and legibly on the 最終確認画面 (the screen just before the
   order-confirm button)** — a link to the terms is NOT enough. Every incumbent
   (ぴあ / ローチケ / e+ / ZAIKO) displays "お客様都合による返品・キャンセル不可".
   Displaying it defeats the 8-day right. Fee disclosure (item 6) does NOT cover
   this; the two are separate MUST items.
8. **Frame the fee as 役務提供の対価, not a 違約金/キャンセル料 (消費者契約法 §9/§10).**
   Define the resale fee in the terms as **consideration for a service already
   rendered** (matching / payment / 本人確認), crystallizing on service completion
   and therefore non-refundable — NOT a penalty for cancellation. This is how
   チケプラ phrases it ("トレード購入手数料 / システム利用料") and lowers §9/§10 void
   risk. Pre-disclose "not guaranteed to sell / ticket returns to you if unsold";
   the original purchase-side processing fee is non-refundable (JP norm).
9. **Cancellation/postponement refund** is a SEPARATE matter from the §15-3
   return right — a voluntary/organizer refund on event cancellation, governed by
   the original ticket's cancellation policy. Keep it distinct from the 返品特約 so
   the two do not contradict (国民生活センター messaging: official resale + a
   cancellation refund guarantee is the consumer-protective selling point).

Market tailwind: after **チケトレ shut down 2025-06-30**, the JP norm is each
primary platform running **its own official resale on its own issuance base**
— exactly Liverty's position (self-issuance + self-resale).

## Money flow detail (ties to ⑤ payments)

- **Match-time (atomic).** When a listed seat matches a buyer, do — in one
  transaction — three things: (1) the buyer's fresh face-value payment settles
  (webhook `payment_intent.succeeded`), (2) the seller's original ticket is
  **voided** (rotating QR invalidated so the seller cannot also enter), (3) a
  **new ticket is issued** to the buyer with 本人確認 re-bound. This prevents
  the seller entering on a seat already resold and never issues a ticket for a
  payment that failed.
- **Seller refund is triggered on resale completion, NOT held to the event (D1).**
  The seller's refund (their own original payment MINUS the resale fee) is
  triggered the moment the resale sells (the atomic match above). The card
  reversal itself is near-immediate; the **net settlement carries a short
  hold-back reserve (~days to ~3 weeks)** as a dispute buffer, then releases —
  **it is NOT tied to the event occurring.** This matches every incumbent with a
  documented timing (ticket board 定価トレード: refund processed the day after the
  trade, bank transfer ~2-3 weeks; e+ ~1-2 weeks; ぴあ ~3 weeks; tiget on 成立 via
  card reversal). **No JP platform holds the seller refund to the event.** Legal
  fit: 資金決済法 2条の2第2号 counter-performance = the seller's **ticket delivery**
  (void+reissue), which completes at match — so paying after match (with a
  hold-back) satisfies the escrow exclusion; holding to the event is unnecessary
  and, per counsel review, weakens rather than strengthens the exemption story.
  Chargeback exposure is managed by the hold-back reserve + delivered-ticket /
  entry-scan evidence + `transfer_reversal`, exactly as incumbents run it.
- **Fee handling (D4).** The reseller bears a **single clean resale fee of ~10%
  of face value** (business-tunable, range 8-12%; benchmarked to ぴあ/ローチケ
  ~10% and covering the ~7.2% round-trip card processing of the refund + fresh
  sale). **⚠️ 消費税/インボイス:** decide whether the 10% is 税抜 (外税) or 税込 — if
  税込 the effective margin drops to ~9.1% after remitting consumption tax, eroding
  the "covers 7.2% + margin" premise; the fee is a 課税取引 subject to 総額表示.
  The **buyer pays exactly face value** — no buyer-side markup. Fee is charged
  **only on a successful resale**; if unsold, no fee and the ticket returns to the
  holder. **"Face value" = the ticket price (券面代金) only** — the original
  purchase-side booking/service fee the seller paid is excluded and non-refundable
  (JP norm). The buyer pays **exactly the 券面代金 with no buyer-side fee** (the
  seller's single ~10% fee is the only charge); the platform collects 券面代金 from
  the buyer, refunds 券面代金 − fee to the seller, and keeps the fee.
- **Escrow / netting.** The buyer's fresh payment to the Organizer replenishes
  the platform balance from which the seller's own refund is issued, so the
  **Organizer settles the seat once** (the original seat's proceeds are refunded
  to the seller and re-collected from the new buyer at the same face value → the
  Organizer's net take for that seat is unchanged, never double-paid). Whether the
  buyer's Organizer-leg payout is itself held-to-event is a ⑤ decision (business
  payee → safe either way); the seller refund does not depend on it.
- **Chargeback / dispute.** Hold a reserve for the hold-back period past the
  dispute window; if a buyer charges back, represent with the delivered-ticket /
  entry-scan evidence and claw back via `transfer_reversal` — same tooling as ⑤.
- **Refund-method failure.** If the seller's original card is expired/closed by
  settlement time (weeks later), the card reversal can fail → fall back to a bank
  transfer / alternative payout to the seller.

## Lifecycle (state machine)

```
             list (before deadline)      offer to next in priority order
  [OWNED] ──────────────────────▶ [LISTED] ──────────────▶ [OFFERED]
     ▲                              │  ▲                        │
     │ withdraw (LISTED only) /     │  │ offer expires,         │ buyer completes
     │ unsold-at-deadline (→EXPIRED)│  │ re-queue (not dead)    │ face-value purchase
     │                              │  └────────────────────────┘
     └──────────────────────────────┘                          ▼
                                                             [SOLD] ──▶ void original
                                                                │  + issue new ticket to buyer
                                                                │  + trigger seller refund (−fee)
                                                                ▼
                                                             [DONE]

  Event CANCELLED while LISTED/OFFERED → cancellation-refund path (leg-2 never ran).
```

- **Eligibility to list:** the ticket's **owner** (the account that holds it),
  for a **PAID, unused** ticket, for a **future event**, **before the resale
  deadline** — **`start_time − 1h`** (matching stops one hour before 開演; D3).
  The Organizer may set an **earlier** cutoff, never a later one. **Precondition:
  ticket sales (and therefore resale) require the event's mandatory info —
  including `start_time` — to be set**; the `start_time − 1h` deadline is
  otherwise uncomputable (the shipped Event entity leaves `start_time` optional,
  so sales acceptance must gate on required-info-complete).
- **`OFFERED` (in-flight) state.** Between LISTED and SOLD a seat is `OFFERED` to
  one candidate with a timed window. **Withdrawal is allowed only in `LISTED`,
  not while `OFFERED`** — this resolves the withdraw-vs-purchase race (the offer
  locks the seat). On offer expiry the seat returns to `LISTED` and re-queues.
- **Re-listing composes:** a resale buyer becomes the new owner and can re-list
  the ticket if they later cannot attend (the model is recursive; LEG 1 refunds
  *their* fresh payment).
- **Companion tickets:** the lead holds N tickets (same-time-entry model); each
  ticket is individually resellable. A resold companion seat is void+reissued to
  the new buyer and **leaves the same-time-entry group** — the new anonymous buyer
  enters independently (the group does not gain a stranger).
- **Unsold at deadline:** the ticket **returns to the holder** (they still attend);
  no fee, no refund — resale is **not guaranteed** (pre-disclosed). *(Decided: MVP
  ships return-only; an organizer-buyback safety net like チケプラTrade is NOT in
  scope.)*

## Matching / anonymity

- **Public resale marketplace with lottery-loser priority (D5).** Resale
  inventory is **publicly visible/joinable** by any buyer (discoverability +
  liquidity, like ぴあ/ローチケ — not hidden behind a pre-registered waitlist). But
  matching order is **priority-ranked, NOT first-come**: **lottery-losers first,
  in draw order**, then the **general public in join order**. A listed seat is
  offered **sequentially** down this ordered queue with a **timed offer**
  (candidate gets a short window; on expiry it passes to the next). This gives
  incumbents' discoverability while keeping the anti-scalp fairness (losers who
  applied and were charged nothing get first refusal; no thundering-herd scramble).
- **Anonymous, no P2P.** Seller and buyer never contact each other or exchange
  personal info; money never goes person-to-person; a buyer cannot designate a
  seller.
- **Match notification is a FUTURE requirement (not MVP).** The DICE model
  push/emails a candidate when their timed offer opens; without it a short window
  is easy to miss. Deferred to a later change; MVP surfaces the offer in-app.

## Domain entities (provider-agnostic, forward-looking)

Reuses ⑤/⑥'s `Order` / `Payment` / `Ticket`. Adds:

- **`ResaleListing`** — `ticket_id`, `seller` (owner at listing), `state`
  (`LISTED`/`OFFERED`/`SOLD`/`WITHDRAWN`/`EXPIRED`), `listed_at`, price = face
  (derived券面代金, not free), resale fee, `matched_buyer`, `sold_at`,
  `refund_settled_at` (post-match hold-back release marker; D1). Money references
  are the seller's original `Payment` (for the refund leg) and the buyer's new
  `Order` (for the sale leg) — no new money primitive.
- **Resale eligibility is a derived property, not an organizer toggle (D2):**
  resale is enabled for every standard paid event by blanket platform-agreement
  consent; a seat is non-resellable only when a **structural exclusion**
  (free/¥0, comp, goods-bundled, name-locked) or an **admin exception** applies.
- **Anti-double-seat / double-charge:** accepting a resale offer **removes the
  candidate from that event's unresolved lottery pool(s)**, and a buyer who
  **already holds a ticket for the event is excluded from the demand queue** —
  enforced against the event's per-person ticket limit across primary + resale.
- **④ dependency — persisted loser ordering:** the "lottery-losers in draw order"
  priority requires ④ `lottery-application` to **persist a stable loser ordering**
  (draw order) that resale can consume; if ④ does not, fall back to
  application-timestamp order. Call this out as a ④ requirement.

## Spec surface (the future `official-resale` change)

RPCs (org-scoped / buyer-facing), to be defined when ④⑤⑥ are specced:
- **Seller:** `ListForResale(ticket_id)`, `WithdrawListing`.
- **Buyer:** join the resale demand queue (or reuse the lottery-loser pool);
  `Buy`/match issues the fresh face-value Order → new ticket.
- **Organizer/admin:** set an earlier resale cutoff; admin structural/exception
  exclusion (resale is mandatory-by-default — there is no per-event enable toggle).
- **Backend:** the match → (settle buyer payment) → (void original + issue new
  + re-bind 本人確認) → (refund seller −fee) transaction; reserve/dispute ops.

## Decisions (settled — carry into the change's design.md)

- **D1 — Seller refund timing: triggered on resale completion, held-back a few
  weeks, NOT tied to the event.** Refund fires at the atomic match (card reversal
  near-immediate); net settlement carries a short hold-back reserve (~days to ~3
  weeks) as the dispute buffer, then releases. **Confirmed against every JP
  incumbent** — ticket board 定価トレード (day-after + ~2-3wk transfer), e+ (~1-2wk),
  ぴあ (~3wk), tiget (on 成立, card reversal); **none hold to the event**. Legal fit:
  2条の2第2号 counter-performance = ticket delivery (void+reissue at match), not the
  event. Chargeback handled by hold-back + delivery/entry evidence +
  `transfer_reversal`. *Reverses the earlier "after-event" lean* — research showed
  hold-to-event is non-standard and (per counsel) weakens, not strengthens, the
  escrow-exclusion story.
- **D2 — Resale is mandatory-by-default, not an organizer opt-in.** Blanket
  consent via the platform agreement enables official resale on every standard
  paid event; no organizer self-serve off-switch. Non-resellable only via
  automatic structural exclusions (free/¥0, comp, goods-bundled, name-locked)
  or a rare admin-approved exception. Maximizes consumer protection + anti-scalp
  coverage and is simpler for MVP (no per-event toggle to build).
- **D3 — Resale deadline: `start_time − 1h`** (matching stops one hour before
  開演), organizer may set an earlier cutoff.
- **D4 — Fee: seller bears a single clean ~10% of face value** (tunable 8-12%);
  buyer pays exactly face value, no buyer-side markup. Covers ~7.2% round-trip
  card processing (refund + fresh sale) plus margin; market-aligned with
  ぴあ/ローチケ. (tiget's ¥220 flat is a low-price-indie artifact — not
  replicable at ¥5,000-10,000 face; it would not cover processing.)
- **D5 — Public resale marketplace with lottery-loser priority (not first-come).**
  Inventory is publicly visible/joinable by any buyer (discoverability + liquidity
  like ぴあ/ローチケ), but matching is **priority-ordered — lottery-losers first
  (draw order), then general public (join order)** — offered sequentially with a
  timed per-candidate window. Combines incumbents' open marketplace with anti-scalp
  fairness. *(Refines the earlier "waitlist-only" lean toward a public marketplace,
  keeping loser priority.)* **Match notification (push/email on offer) is deferred
  to a future change.**
- **D6 — Unsold = return-only (no organizer buyback in MVP).** If a listing does
  not sell by the deadline the ticket returns to the holder; no buyback safety net
  (チケプラTrade offers one — deferred).
- **D7 — Mandatory-by-default holds even against an artist no-resale rider;
  handled by the admin exception (not an organizer self-serve switch).** An
  Organizer bound by an upstream no-resale contract is covered by the rare
  admin-approved exclusion (D2), which is sufficient for MVP.

## Counsel brief (resale-specific — add to the #778 legal track)

1. Confirm the **void-original + refund-seller + fresh-face-value-sale** structure
   avoids 資金移動業 via **BOTH** grounds: (a) buyer leg = 収納代行 to a **business
   Organizer** (代理受領, buyer debt extinguished at payment), and (b) seller leg =
   a **refund of the seller's own PaymentIntent** that also fits **資金決済法 2条の2
   第2号 (escrow exclusion)** — funds received before/with the **counter-performance
   (= the seller's ticket delivery via void+reissue, NOT the event)** and moved to
   the seller **after** it. Confirm specifically that **settling the seller a few
   weeks after the match (not holding to the event)** is the correct/safe timing
   and that hold-to-event is NOT required (and does not strengthen the exemption).
   Confirm the "refund of own money" framing vs a "代金交付" framing — which is
   cleaner given the buyer funds the balance.
2. Confirm **古物営業法** does not require a licence for a **no-inventory,
   organizer-consigned, electronic-ticket** official resale (void+reissue,
   platform never buys/stocks) — and the boundary if physical tickets are ever
   handled (→ 金券類 古物商許可).
3. Confirm the **特商法 / 消費者契約法** treatment of the resale fee and the
   "not guaranteed / non-refundable-if-unsold" clause (fee = listing-service
   consideration; clear pre-disclosure).
4. Confirm the **本人確認 re-bind** on reissue keeps the reissued ticket a
   protected 特定興行入場券 for the new holder.
5. Confirm the **blanket, standing resale consent** taken in the vetted-Organizer
   platform agreement (D2) satisfies the チケット不正転売禁止法 "organizer
   consent" requirement for **all** of that Organizer's events, so mandatory-by-
   default resale is not an "unauthorized" transfer — and that no per-event
   re-consent is legally required. Flag the **artist/promoter no-resale rider**
   edge (D7): an Organizer cannot consent where an upstream contract forbids
   resale; confirm the **admin-exception** carve-out is the adequate mechanism.
6. Confirm the **特商法 §12-6 (令和3年改正) 最終確認画面 返品特約 display** (返品不可)
   for the buyer's 通信販売 purchase defeats the §15-3 8-day return right, and that
   this is **required separately from the fee disclosure**. Confirm the **fee =
   役務提供の対価 (not 違約金/キャンセル料)** framing lowers 消費者契約法 §9/§10 void risk.
7. Confirm the **個人情報保護法** handling of captured/re-bound 本人確認 (name+contact
   of both parties): 利用目的の特定 (resale as a purpose), retention through the
   dispute/hold-back window then **deletion**, and that keeping the parties
   anonymous to each other avoids §27 第三者提供. Define a retention schedule.
8. **消費税 / インボイス** on the resale fee (課税取引): decide 税抜/税込 and 総額表示;
   confirm output-tax remittance and whether a 適格請求書 is needed (most sellers are
   consumers → no 仕入税額控除 need, but presentation must be correct).
9. **令和7年 (2025) 資金決済法改正 (施行 令和8年6月):** confirm the narrowed 収納代行
   / cross-border rules do **not** pull this domestic resale flow into 為替取引; the
   #778 brief was drafted pre-amendment.

## References

- Legal: 文化庁 チケット不正転売禁止法; e-Gov 平成30年法律103号; 古物営業法
  (金券類 / 委託・在庫なし例外); 国民生活センター / 消費者庁 (viagogo 注意喚起,
  公式リセール推奨); ACPC チケット適正流通協議会.
- Market: `market-design-notes.md`; チケトレ closure (2025-06-30, Impress /
  音楽ナタリー); ぴあ / ローチケ / e+ / ticket board (チケプラTrade) resale help.
- Payments: `payments-design.md` (issue #778) — shared Stripe Connect /
  収納代行 scheme, refund + `transfer_reversal`.
