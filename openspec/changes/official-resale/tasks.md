## 0. Dependency gate (must clear before any implementation)

- [ ] 0.1 Confirm ④ `lottery-application` is specced + shipped, and **persists a stable loser ordering (draw order)** that resale can consume (fallback: application-timestamp order)
- [ ] 0.2 Confirm ⑤ `ticket-purchase-and-issuance` is specced + shipped (Order/Payment/Ticket + Stripe Connect 収納代行 + refunds/`transfer_reversal`)
- [ ] 0.3 Confirm ⑥ `ticket-wallet-and-checkin` is specced + shipped (issue / void / rotating-QR / 本人確認 binding)
- [ ] 0.4 Confirm legal counsel sign-off on the 9-item resale brief in #778 (escrow-exclusion 2条の2第2号 + post-sale settlement; no-inventory 古物; 特商法 fee clause; 本人確認 re-bind; blanket-consent incl. artist-rider/admin-exception; 返品特約 §12-6; 個人情報 lifecycle; 消費税/インボイス; 2025資金決済法改正)

## 1. Ticket-type metadata + sales gate (⑤/⑥ extension)

- [ ] 1.1 Add resale-eligibility metadata to the Ticket entity: is-free/¥0, comp/invite, goods-bundled, name-locked flags (structural-exclusion source)
- [ ] 1.2 Add the per-event resale cutoff field (default `start_time − 1h`, organizer-configurable earlier)
- [ ] 1.3 Carry the Organizer blanket-consent flag from the platform agreement onto the event's resale-enabled state
- [ ] 1.4 Gate ticket sales/resale on **required event info (incl. `start_time`) being set** (deadline otherwise uncomputable)

## 2. Proto / entity (specification repo → BSR)

- [ ] 2.1 Define the `ResaleListing` entity (ticket_id, seller, state LISTED/OFFERED/SOLD/WITHDRAWN/EXPIRED, listed_at, derived face price=券面代金, resale_fee, matched_buyer, sold_at, refund_settled_at) referencing existing Payment/Order
- [ ] 2.2 Define seller RPCs: `ListForResale`, `WithdrawListing` (LISTED-only) (org/buyer-scoped auth)
- [ ] 2.3 Define buyer-side RPCs: join the public resale demand queue + timed-offer accept
- [ ] 2.4 Define organizer/admin RPCs: earlier-cutoff config, admin structural/exception exclusion
- [ ] 2.5 protovalidate constraints (face-value lock, deadline, state transitions incl. OFFERED lock); buf lint/breaking; merge spec PR → GitHub Release → BSR gen

## 3. Backend — listing lifecycle

- [ ] 3.1 Implement listing eligibility (owner, PAID+unused, future event, resale-enabled, before deadline, required-info set; reject structurally-excluded)
- [ ] 3.2 Implement `ListForResale` (price derived = 券面代金) and `WithdrawListing` (LISTED only; rejected while OFFERED/SOLD)
- [ ] 3.3 Enforce the `start_time − 1h` deadline (+ organizer earlier cutoff); EXPIRE + return-to-holder job at deadline (no fee, no refund = D6 return-only)
- [ ] 3.4 Re-listing composes (a resale buyer can re-list as the new owner)

## 4. Backend — public marketplace + matching

- [ ] 4.1 Build the priority-ordered demand queue (lottery-losers by draw order, then general public by join order); public discoverability/join
- [ ] 4.2 Sequential timed-offer engine (OFFERED lock per candidate; expiry → next; queue-exhausted-before-deadline → back to LISTED, not dead); anonymity (no seller designation)
- [ ] 4.3 Atomic match transaction: settle buyer face-value payment → void original ticket (invalidate QR) → issue new ticket + re-bind 本人確認 (all-or-nothing); failed payment leaves listing LISTED
- [ ] 4.4 Anti-double-seat: on offer-accept remove the candidate from that event's unresolved lottery pool(s); exclude existing-holders from the queue (per-person limit across primary+resale)
- [ ] 4.5 Resold companion seat leaves the same-time-entry group (new buyer enters independently)

## 5. Backend — money legs (reuse ⑤ payments)

- [ ] 5.1 Charge the seller-side resale fee (~10%, configurable; **rounding rule + clamp to refundable amount**; framed as 役務対価; decide 税抜/税込) only on successful resale; disclose pre-listing
- [ ] 5.2 Trigger the seller refund (original 券面代金 − fee) **on resale completion** with a short hold-back reserve; **NOT gated on the event**; refund-method fallback (bank transfer) if the original card can't be reversed
- [ ] 5.3 Chargeback handling: draw on hold-back reserve, represent with delivered-ticket/entry evidence, `transfer_reversal` clawback
- [ ] 5.4 Netting so the Organizer settles the seat once (buyer payment replenishes the balance the seller refund is drawn from)

## 6. Frontend (Aurelia PWA)

- [ ] 6.1 Seller: list / withdraw (LISTED only); show settlement timing (post-sale hold-back) + "not guaranteed" + fee disclosure (特商法 表記)
- [ ] 6.2 Buyer: browse public resale inventory + join queue; timed-offer accept + face-value checkout
- [ ] 6.3 Buyer: **返品特約 (no-return clause) on the final confirmation screen** (特商法 §12-6), distinct from fee disclosure
- [ ] 6.4 State surfaces (LISTED/OFFERED/SOLD/EXPIRED) and reissued-ticket wallet update

## 7. Compliance surfacing

- [ ] 7.1 Covered-ticket (特定興行入場券) face conditions on original + reissued ticket; 本人確認 captured on reissue
- [ ] 7.2 特定商取引法に基づく表記: resale fee (single %, no cap), any seller-side transfer fee, per-Organizer 事業者情報 on confirmation
- [ ] 7.3 個人情報 lifecycle: 利用目的 (resale), retention through hold-back/dispute window, then deletion of the voided seller's 本人確認

## 8. Release & verification

- [ ] 8.1 Cross-repo release order: spec → BSR → backend → frontend; provision any new consumers/streams
- [ ] 8.2 End-to-end verify: list → (public queue, loser priority) match → void+reissue → **seller refund on completion (hold-back)**; queue-exhausted-alive; unsold-return; cancellation + postponement paths; anti-double-seat
- [ ] 8.3 Sync delta specs to main specs and archive the change

## 9. Future (out of MVP scope — do not implement now)

- [ ] 9.1 Match-turn notification (push/email when a candidate's timed offer opens; DICE model)
- [ ] 9.2 Organizer buyback of unsold listings (チケプラTrade-style safety net)
