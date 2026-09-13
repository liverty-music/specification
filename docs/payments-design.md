# Payments Design (Phase 3 ⑤)

Durable design for the ticket **payment** track — the input to the roadmap
change `ticket-purchase-and-issuance` (⑤). Consolidates the research and
decisions tracked in issue liverty-music/specification#778 so they are not
lost in ephemeral notes. Not legal advice — the counsel flags below must be
confirmed before launch.

Grounded in `ticketing-platform-roadmap.md` (Deferred Payment Details) and
the competitor/market research in `market-design-notes.md`.

## Decisions (settled)

- **Provider: Stripe Connect.** Chosen for breadth + DX. Money is
  **platform-intermediated** (Liverty collects, takes a fee, pays out the
  Organizer). *Challenger to PoC:* **KOMOJU (Degica)** is arguably a better
  fit for a JP lottery (authorize→split-at-capture, deepest JP methods) —
  run a serious PoC before locking in. Adyen for Platforms is the
  enterprise-scale "graduation" target.
- **Connect charge model: separate charges & transfers (platform-held escrow) —
  SUPERSEDES the earlier destination-charge decision (see "Why separate charges
  & transfers" below).** The platform charges the buyer (funds sit on the
  **platform** balance), then **`Transfer`s the Organizer's net share after the
  event** (`source_transaction` links each transfer to its charge); losers' holds
  are released and refunds come from the platform balance. This is what actually
  realizes **hold-to-event escrow** — a destination charge settles to the
  Organizer's balance immediately at capture (manual payout only delays the
  Organizer's *bank* withdrawal, not platform custody). **Payee model = single
  Organizer + retained platform fee**, modelled as extensible splits (venue is the
  Organizer's cost, not a platform payee — the ticketing norm). **Three axes stay
  separate** (do not conflate): legal seller-of-record = **Organizer** (via 収納代行
  contract + 特商法 表記); money-handling role = **platform as 収納代行 collection
  agent** (代理受領権限); Stripe settlement-merchant/MoR = **the platform** (MVP: **no
  `on_behalf_of`**). Naming the Organizer via `on_behalf_of` would require its connected
  account to hold the `card_payments` capability active **before** the charge, gating
  ticket sale on merchant KYB — so MVP keeps the platform as the Stripe merchant and carries
  seller-of-record contractually. The statement stays recognizable via the platform static
  prefix + a per-event dynamic suffix (kanji/kana); Organizer-named statement is a future
  `on_behalf_of` change if counsel requires it. The full settlement mechanics are specified
  in the **`ticket-settlement-and-payout`** change. `allocated_funds` fund isolation is
  **not adopted** (JP-ineligible — see below).
- **Methods: card-only for MVP** (incl. **debit / prepaid** cards — the
  cardless-fan substitute — and Apple Pay / Google Pay, which are just
  `card` wallets). **Konbini / PayPay are out of scope** for MVP (async
  settlement, ¥300k caps, PayPay's Connect incompatibility). The domain
  entity is provider- and method-agnostic, so they can be added later
  without a proto break. Trade-off: card-only excludes some cardless
  students/minors — accepted for a vetted-partner MVP, revisit on demand.
- **Lottery charge mechanism: authorization hold (Stripe manual-capture) —
  SUPERSEDES the earlier SetupIntent decision (see Why, updated).** At application,
  **authorize (hold) the ticket amount** via a manual-capture `PaymentIntent`
  (`capture_method=manual`, 3DS once). At the draw, **capture winners / cancel
  (release) losers**. ④ owns authorize+capture; ⑤ takes the captured payment →
  Order + Ticket. **JPY cards only, American Express excluded** — a **JP-based
  Stripe account holds JPY card authorizations up to 30 days**, ≫ the 1–14-day
  lottery window, so the hold survives to the draw. **No payment deadline, no
  off-session charge, no re-auth/grace, no 繰上げ** — a held authorization captured
  at the draw effectively does not fail (a rare failed capture → seat unfilled,
  manual follow-up).
- **Payout: hold to event + dispute window (platform-held via separate charges
  & transfers).** Buyer funds sit on the **platform** balance from capture; a
  **scheduled platform process** `Transfer`s the Organizer's net share only
  **after the event AND a dispute-safety buffer** (chargebacks arrive
  days-to-weeks later — "after event" alone is too early). Refunds/releases come
  from the platform balance (`Refund`; `transfer_reversal` claws back a share
  already transferred). This genuinely holds funds until counter-performance —
  unlike a destination charge + manual payout, which only delays the Organizer's
  bank withdrawal of funds already in its own balance.
- **Webhooks are the source of truth** for capture / refund / dispute — never
  issue tickets on the client confirm alone. Idempotent handlers.
- **Fee model: a flat percentage, buyer-shiftable.** A single clean % (like
  LivePocket's flat 5%) reads better than a stacked per-ticket fee (tiget's
  ¥220+¥99 draws complaints). Buyer-pass-through toggle → organizer cost can
  be ¥0. Exact rate is a business decision (#778).

### Why authorization hold (updated — reverses the earlier SetupIntent reasoning)

The earlier design chose SetupIntent because a **full-amount hold was assumed too
short-lived** (the standard **~7-day** authorization) to survive a lottery window,
and holding across the many lotteries a fan enters would 与信枠圧迫. That premise was
**wrong for our case**: a **JP-based Stripe account holds JPY-card authorizations
for up to 30 days** (Visa/Mastercard/JCB/Diners/Discover), and the lottery window is
bounded to **1–14 days** (④, default 10), comfortably inside 30. So a manual-capture
hold **does** survive to the draw, and it **removes the machinery SetupIntent
needed**: no off-session charge that can fail, no payment deadline, no re-auth/grace
link, no **当選無効 → 繰上げ**. Trade-offs accepted: (a) the fan's funds are held for
the window (bounded ≤14 days; the ローチケ norm), and (b) **American Express + non-JPY
cards are excluded** (they fall back to the ~7-day window, too short) — rejected at
application in ④. This is the model ④ `lottery-application` implements; ⑤ consumes
the **captured** payment.

> Historical note: the original "Why SetupIntent" argument (¥1 validity check at
> apply, auto-charge winners at draw, prepaid/debit hold-release in 1–8 days) applied
> to the **non-JPY / generic** hold; the JPY-30-day window is the specific fact that
> reversed it. Prepaid/debit that cannot hold 14 days are excluded like Amex.

### Why separate charges & transfers (escrow mechanism) — hold-to-event custody

The **hold mechanism** (manual-capture authorization, above) and the **escrow
mechanism** (who custodies the captured funds until the event) are different axes.
For the escrow mechanism, **separate charges & transfers** is correct — **not**
destination charges:

- **Destination charges settle to the Organizer immediately at capture.** Stripe
  moves the full amount to the connected account's balance the moment the charge is
  captured; manual payout only delays the Organizer's *bank* withdrawal. So a
  destination charge does **not** give the platform custody and cannot back a
  "hold-to-event escrow" claim.
- **Separate charges & transfers holds funds on the platform balance** until a
  scheduled post-event `Transfer` to the Organizer (`source_transaction` ties each
  transfer to its charge). This is Stripe's documented pattern for "create the
  charge before you're ready to move the funds", and it is what genuinely realizes
  hold-to-event escrow, ⑦ resale re-routing, and loser refunds from a pooled
  balance.
- **Competitor corroboration.** Every JP incumbent (Peatix / ぴあ / TIGET / ZAIKO /
  LivePocket) and the clearest global Stripe example (Eventbrite) operate as
  *platform collects → holds until after the event → post-event settlement to the
  organizer* — the separate-charges shape, under a 収納代行 / 委託販売 wrapper.
- **The "収納代行 vs true escrow" framing is a false dichotomy.** Platform-held funds
  (separate C&T) are compatible with the Organizer remaining the legal
  seller-of-record: 代理受領権限 discharges the buyer's obligation at payment, so the
  platform holding those collected funds until the event is normal collection-agency
  behaviour. Keep the three axes separate but decoupled from any Stripe flag
  (seller-of-record = Organizer *contractually*; money-handling = platform 収納代行 agent;
  Stripe settlement-merchant = **the platform**, no `on_behalf_of`).
- **Stripe settlement merchant = platform; NO `on_behalf_of` (updated).** The earlier plan
  adopted `on_behalf_of` = Organizer so the descriptor/settlement would follow the seller.
  Stripe's mechanics make that unworkable for MVP: putting the Organizer's name on the
  statement requires its connected account to hold the **`card_payments` capability active
  before the charge** ("連結アカウントから静的コンポーネントを使用するには card_payments
  ケイパビリティが必要") — i.e. before the lottery authorization at application time — which
  would gate ticket sale on full merchant KYB and contradict "onboarding never blocks sale."
  Stripe's own Connect guidance also lists `on_behalf_of` as a trap for standard
  separate-charges flows and says NOT to request `card_payments` for a recipient account.
  So MVP uses a lightweight `transfers`-only recipient and keeps the platform as the Stripe
  merchant. Cost of dropping `on_behalf_of` = only the statement *prefix name* (platform vs
  Organizer); recognizability (per-event suffix incl. kanji/kana), settlement country (all
  domestic → identical), fees (all-JP → identical), and **chargeback liability (on the
  platform under either model)** are unchanged. This matches the JP incumbents (Peatix/ZAIKO
  show the platform on the statement and operate as 収納代行). Organizer-named statement =
  future change (merchant onboarding + pre-sale gating) if counsel requires it.
- **Trade-offs accepted.** Higher ops complexity (manage charge → hold → per-split
  `Transfer` → reversals; the platform must accept connected-account **negative-balance
  responsibility** — also a prerequisite for funds segregation).
- **Stripe funds segregation (`allocated_funds`)** is the purpose-built primitive to
  isolate held separate-charge funds from platform payouts / other refunds / fees.
  Availability is gated on **three separate conditions**, not just an API version:
  (1) opt into the preview API surface (`Stripe-Version: 2026-08-26.preview;
  allocated_funds_preview=v1` on every request) — necessary but **not** sufficient;
  (2) **access grant** — it is a *private* preview (not self-serve), so Stripe must
  **allowlist the platform account** (contact the account manager); (3) **market
  eligibility** — the platform account's market must be supported, and the listed
  markets are **BE/CH/DE/DK/ES/FR/GB/NL/SE/US only — JP is not among them**. So the
  preview header alone does **not** unlock it for a JP platform. **Ship plain separate
  charges & transfers first** (fully GA in JP; funds sit in the general platform
  balance until the Transfer); adopt `allocated_funds` only if Stripe grants JP access
  + the market opens (confirm timeline + that single manual-capture is supported —
  docs imply yes, only multicapture/overcapture/incremental-auth are excluded — with
  the account manager).

> **✅ ④ reality check (corrected — no follow-up needed).** A read of the shipped
> backend (`internal/infrastructure/payment/stripe_authorization.go`) confirms ④
> `lottery-application` charges with a **plain platform-account** manual-capture
> `PaymentIntent` — **no `TransferData` / `OnBehalfOf` / `ApplicationFee`**, i.e. **not**
> a destination charge. So captured funds **already land on the platform balance** (the
> "charge" half of separate charges & transfers is already correct); there is **nothing
> to migrate in ④**. The earlier "④ shipped a destination charge → migrate" note was
> **factually wrong** and is withdrawn. What is genuinely **unbuilt** is the "transfers"
> half — Organizer Connect onboarding, the post-event `Transfer` (single-Organizer split
> + retained platform fee), refund/`transfer_reversal` — now specified as the
> **`ticket-settlement-and-payout`** capability. Gate before a live paid sale alongside
> the counsel opinion (flag 1).

## Legal / money scheme (収納代行) — not legal advice

- **収納代行 (collection agent) + intermediary marketplace; Organizer =
  seller-of-record.** Avoid MoR, 資金移動業, 前払式支払手段.
- Buyer ToS: the buyer's obligation is **discharged on paying the platform**.
  Organizer contract: grants the platform **代理受領権限**.
- **前払式 avoidance:** charge a **specific-event ticket at win, deliver
  promptly** — no wallet / points / stored balance.
- **特商法:** Organizer is the **販売業者** (own 特商法 表記 / group page). The
  **final-confirmation screen (2022)** must state total (tax+fees) and the
  **charge timing** — for lottery: "charged only if you win, at the draw;
  card saved for that later charge." Log consent + timestamp (also MIT /
  dispute evidence).
- **未成年:** DOB + parental-consent notice (an "18+" button is legally
  insufficient); own-name card implies consent.
- **Refund norm:** on cancellation refund face value + system/発券 fee, but
  **keep the payment-processor fee** (JP standard).
- **景品表示法 / 賭博: fine as designed** — paid 抽選販売 is allocation of the
  purchased ticket, not a 懸賞/景品, and not 賭博 since **losers pay ¥0**.
  Guardrails: losers pay nothing; no purchase-scaled free bonus; wording
  "抽選販売", not "prize".

### 収納代行 determination — likely exempt (refined, 2025-2026 legal + market check)

**Why the license question exists at all:** moving other people's money
between remote parties (為替取引, 最決平成13年) is a licensed monopoly (bank
or 資金移動業). Operating unlicensed is **criminal** (銀行法 §61: up to 3yr /
¥3M, corporate 両罰 up to ¥300M) — which is why the boundary must be
*confirmed*, not assumed. 収納代行 is exempt because the buyer's debt is
**discharged on payment to the agent** → no protectable "money in flight".

**Our flow most likely sits in the exempt zone**, on two structural facts:
1. **Payee = business.** The 2020 amendment (施行 2021-05) pulls collection
   into 資金移動業 only when the **payee (受取人) is an individual acting in a
   non-business capacity** (割り勘 / C2C). Our Organizers are vetted
   **事業者** sellers-of-record → outside that trigger, so the traditional
   exemption holds.
2. **Domestic-only.** The 2025 amendment (公布 2025-06; 施行 ~2026) that newly
   regulates **cross-border 収納代行** applies to 国内⇄国外 flows only. A
   fully domestic buyer/platform/Organizer flow is untouched.

**Market corroboration:** holding buyer funds **until after the event** and
**charging lottery winners at the draw via a saved card** are the **universal
JP ticketing norm** (LivePocket, tiget, ZAIKO, Peatix, teket, e+/ぴあ/ローチケ
— none pays the organizer pre-event). **ZAIKO's terms explicitly operate as
収納代行 with the Organizer as seller and "immediate charge of the registered
card at the time of winning"** — essentially our design. So our hold-until-
event is **not** an anomaly; it is established practice, which supports the
escrow characterization rather than undermining it. The **only** genuine
divergence from incumbents is the **PSP rail** (Stripe Connect vs domestic
GMO/proprietary/イーコンテクスト) — a technology choice, not a business-model
one; Stripe Connect realizes the held-until-event settlement the incumbents get
from delayed acquiring via **separate charges & transfers** (funds held on the
platform balance, transferred post-event) — a destination charge + manual payout
would **not** hold funds (it only delays the Organizer's bank withdrawal), so
separate charges & transfers is the correct rail for this model.

**Safe-harbor to stay clearly in exempt 収納代行** (structure in the contract
stack + T&Cs):
1. **Payee = 事業者** — contract/vet the Organizer as a business seller;
   never settle to a private individual.
2. **Discharge clause (load-bearing)** — buyer ToS: obligation **discharged
   on payment to the platform**; Organizer grants **代理受領権限**.
3. **Genuine underlying transaction** — a real ticket sale by the Organizer;
   platform = collection agent (keep the substance documented).
4. **Hold = escrow-with-counter-performance** — release gated on the
   **event occurring / ticket honored**, with evidence retained. (There is
   **no bright-line safe N-day** in the rules; safety comes from the
   discharge + counter-performance gate, not the length — this reframes the
   old "hold-duration" flag.)
5. **Collection via the licensed PSP** (Stripe).
6. **Stay domestic** — a foreign Organizer or offshore fund routing crosses
   into the 2025/2026 cross-border regime → re-analyze.

Points 1/5/6 are self-assessable; **2/3/4 need a written 弁護士 opinion**
(fact-specific + criminal downside).

## Counsel flags (confirm before launch)

1. **⚠️ 収納代行 exemption opinion (highest leverage — closes 資金決済法 +
   犯収法 together).** Get a written opinion confirming: (i) the discharge
   clause is effective and the platform is a collection agent (not
   seller/MoR), (ii) the **hold-until-event** design qualifies as exempt
   escrow (府令第1条の3, non-為替取引 / not 預り金), and (iii) no cross-border
   leg exists. Likely exempt (business-payee + domestic; see determination
   above), but the escrow/discharge boundary is where the FSA applies
   substance-over-form.
2. **Seller-of-record ↔ UX alignment** — if marketing/UX makes the *platform*
   look like the seller, the collection-agent theory weakens. Align the
   legal structure with the UX (Organizer named as 販売業者 at checkout).
3. Charge-after-win card-on-file + MIT — confirm no 割賦販売法 / 前払式 issue.
4. MoR / 特商法 seller-of-record + domestic-fee 課税 (10%) → register as
   適格請求書発行事業者; 媒介者交付特例 only if organizers are registered.
5. 消費者契約法 enforceability of refund/cancellation clauses.

### Official-resale counsel addenda (from `resale-design.md`)

Resale-specific items for the same #778 legal track. Full design +
research: [`resale-design.md`](./resale-design.md). "Δ" marks where the
resale analysis differs from or extends the primary-sale analysis above.

1. **⚠️ 資金移動業 for the resale money legs (highest leverage).** Resale is
   **two decoupled legs**: (a) buyer→Organizer fresh face-value sale =
   the same 収納代行/事業者-payee scheme as the primary sale (may hold to
   event); (b) seller refund = a **refund of the seller's own payment**.
   Confirm leg (b) avoids 資金移動業 via **both** grounds: it is a refund
   (not a payee transfer) AND, if the seller is nonetheless viewed as an
   individual payee, it fits the **資金決済法 2条の2第2号 escrow exclusion**
   (funds received before/with counter-performance, moved to the payee
   **after counter-performance = the seller's ticket delivery via
   void+reissue**). **Δ vs primary:** the seller-refund leg is **settled
   ~days-to-3-weeks after the resale completes, NOT held to the event** (ぴあ
   /ticket board/e+/tiget norm) — so the primary "hold-until-event" escrow
   framing does **not** govern this leg; confirm the "refund of own money"
   vs "代金交付" framing given the buyer funds the balance.
2. **古物営業法** — confirm **no 古物商許可** for a **no-inventory,
   organizer-consigned, electronic-ticket** resale (void-original + reissue,
   platform never buys/stocks); and the boundary if physical tickets are ever
   handled (→ 金券類 古物商許可).
3. **不正転売禁止法 — blanket organizer consent.** Confirm the **standing
   consent** in the vetted-Organizer platform agreement satisfies the
   興行主の同意 requirement for **all** that Organizer's events (no per-event
   re-consent needed), so mandatory-by-default resale is not "unauthorized".
   Flag the **artist/promoter no-resale rider** edge — an Organizer bound
   upstream cannot consent; confirm the **admin-exception** carve-out suffices.
4. **本人確認 re-bind keeps 特定興行入場券.** Confirm reissuing with the new
   holder's 本人確認 (name+contact) + the 3 face conditions preserves the
   covered-ticket protection for the new owner.
5. **特商法 §12-6 返品特約 on the buyer's 最終確認画面 (Δ: distinct from the
   fee disclosure)** — the resale buyer's fresh purchase is a 通信販売;
   displaying 返品不可 defeats the §15-3 8-day return right. **Frame the
   resale fee as 役務提供の対価 (not 違約金/キャンセル料)** to lower 消費者契約法
   §9/§10 risk on the "non-refundable / not-guaranteed-if-unsold" terms.
   (Extends counsel flag #5 and obligations-table #2 to the resale leg.)
6. **個人情報保護法 — 本人確認 lifecycle (Δ).** Define 利用目的 (resale as a
   purpose), retention through the hold-back/dispute window, then **deletion**
   of the voided seller's 本人確認; both-party anonymity avoids §27 第三者提供.
   (Beyond the Stripe 越境移転 item in obligations-table #4.)
7. **消費税 / インボイス on the resale fee (Δ).** The seller-side ~10% fee is
   課税取引 under 総額表示; decide **税抜 vs 税込** — if 税込, effective take is
   ~9.1% after consumption tax, which affects the fee-band choice.
8. **令和7年 (2025) 資金決済法改正 (施行 ~令和8年6月).** Confirm the narrowed
   收納代行 / cross-border rules do **not** pull this domestic resale flow into
   為替取引; this brief predates the amendment.

## Domain entity (provider-agnostic)

Order/Payment carries only: `provider` (stripe), opaque `payment_intent_id`
(`pi_…`) + `payment_method_id` (`pm_…`), `payment_method_type` (card now;
konbini/paypay later), own `status` (`paid` on creation → `refunded`, or
`failed` for the capture-succeeded-but-issuance-refunded edge — **no `pending`**:
⑤ creates the Order from ④'s already-captured payment, and no `awaiting_payment`
now that konbini is out), `amount`+`currency`,
`paid_at`, optional display facets (`card_brand`/`card_last4`). Never store
PAN/CVC/expiry or Stripe's raw status. This keeps ⑤'s proto stable across a
provider switch (KOMOJU) or added methods.

## Open decisions (business / counsel, long lead — start now)

- KOMOJU-vs-Stripe PoC outcome; Stripe Connect account type + KYC/審査 apply.
- MoR designation + 特商法 seller wording; fee rate; payout schedule
  (event-end-keyed, like the incumbents — the escrow *gate* matters, not a
  bright-line duration); refund/cancellation policy; 適格請求書発行事業者
  registration.

## Regulatory compliance obligations (JP) — beyond the 収納代行 scheme

Additional obligations surfaced by the 2026-08 legal sweep (issue #778).
Not legal advice — confirm the flagged items with counsel. **Owner** = who
implements/holds the duty.

| # | Obligation | Blocking | Owner | What to build / disclose |
|---|-----------|----------|-------|--------------------------|
| 1 | **総額表示義務** (消費税法 §63, since 2021-04) | **Yes** | Platform | Render every consumer-facing price **tax-inclusive** (ticket AND system/payment fee, each as its own 税込 line) + a clear grand total on listing/cart/confirmation. |
| 2 | **特商法 通信販売: 最終確認画面 + 返品特約 + no cooling-off** (§11, §12-6 2022) | **Yes** | Platform (screen) / Organizer (事業者情報) | Confirmation screen showing 分量・価格(税込)・**支払時期方法**・**引渡時期**・**返品特約**・per-Organizer **事業者情報**; make the **charge-on-lottery-win timing/amount unambiguous**; state "通信販売 = クーリングオフ無し". **Omitting 返品特約 triggers an 8-day statutory return right** — so spell out "no returns except event cancellation/postponement". |
| 3 | **割賦販売法 (2018): card-data 非保持化 / PCI** | **Yes (precondition)** | Platform (加盟店) / Stripe | Stripe Elements so **no PAN touches our systems** (store only Stripe tokens/customer ids — incl. the saved-card-at-draw flow); keep **PCI SAQ A** + EMV 3DS on file. |
| 4 | **個人情報保護法 (2022): 越境移転 to Stripe (US)** | **Yes** | Platform | Privacy policy: personal/card data is **entrusted (委託) to an overseas processor (Stripe, USA)** + **外的環境の把握** (US regime + Stripe safeguards); hold a **Stripe DPA** as 委託先監督 evidence. |
| 5 | **犯収法 / AML-KYC** | Confirm | Stripe (card-level) | A pure 収納代行 that does **not** perform 為替取引 is generally **not** a 犯収法 特定事業者. Document why the flow is 収納代行, not remittance. **Same determination as the 資金決済法 boundary** — close it once. |
| 6 | **反社会的勢力排除 (暴排条例)** | **Yes** | Platform | Organizer onboarding contract with a **暴排条項** (表明保証 + immediate termination) + a **反社チェック** step in vetting. *(Belongs to the organizer-accounts vetting flow — cross-reference.)* |
| 7 | **電子帳簿保存法 (2024 電子取引 mandatory)** | From day one | Platform | Retain fee invoices/receipts/transaction records electronically with **真実性 + 可視性** (searchable by date/amount/counterparty). |
| 8 | **領収書 + 印紙税 / 適格請求書** | Low | Organizer (ticket) / Platform (fee) | Receipts must **print "クレジットカード決済"** → 印紙-free at any amount. 適格請求書: Organizer 登録番号 on the ticket, platform 登録番号 on the fee (代理交付/媒介者交付特例). |

**Highest-leverage counsel question (closes #5 + reinforces 資金決済法):**
confirm our payout timing/holding keeps 収納代行 **out of 為替取引 /
資金移動業** — this single determination decides both the license question and
whether 犯収法 KYC applies to the platform.

## Commerce spec still to define (in ⑤ `ticket-purchase-and-issuance`)

Non-regulatory gaps to specify when ⑤ is authored:

- **Pricing model:** Organizer-set price, JPY, tax-inclusive, ticket tiers
  (adult/child sharing the capacity pool), any price cap.
- **Order ↔ Ticket ↔ Payment linkage:** one Order = N tickets (companion,
  ≤ `max_tickets_per_application`); a successful charge issues N tickets.
- **Refund taxonomy:** **postponement (延期, event still happens) vs
  cancellation (中止)**, partial refunds, and the "no returns except
  cancellation" 返品特約 wording (ties to §2 above).
- **Payout mechanics:** payout schedule, per-Organizer **settlement
  statement (支払明細)**, failed-payout + negative-balance handling, Stripe
  KYC bank onboarding.
- **Dispute/chargeback ops:** evidence/representment, Organizer↔platform
  liability split via `transfer_reversal`, reserve past the dispute window.
- **Platform-fee 適格請求書** to the Organizer + Stripe-balance
  reconciliation.
- **Webhook security** (signature verification) + idempotency keys; a
  **test/sandbox** strategy for the lottery charge flow.
- **Purchase limits** (1 account / 1 application) enforced at the
  payment/order layer (anti-scalp).

## References

- Tracking + research log: issue liverty-music/specification#778.
- Market/competitor design: `market-design-notes.md`.
