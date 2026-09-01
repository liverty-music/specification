# Ticketing Platform Roadmap

This document decomposes **Phase 3 (Platform Expansion)** of
[`product-design.md`](./product-design.md) — the organizer-facing ticket
sales & management system — into a sequence of independently shippable
OpenSpec changes.

It exists because Phase 3 is large enough that a single OpenSpec change
cannot hold it, and a roadmap spanning many future changes belongs in
`docs/` (project strategy), not in `openspec/` (which tracks the current
capability truth and individual deltas). Each change listed here is
created with `/opsx:propose` **when work on it actually starts** — do not
pre-create empty change stubs.

Primary source for the ticketing technical direction (Web2, no
blockchain) is the decision record in `product-design.md` and
`openspec/changes/archive/2026-08-09-remove-blockchain-ticket-system/`.

Companion durable docs: [`payments-design.md`](./payments-design.md)
(the ⑤ payment design + legal scheme) and
[`market-design-notes.md`](./market-design-notes.md) (2025-2026
competitor/market check + the roadmap calibrations it drove).

## Guiding Decisions (settled)

These answers scope the entire roadmap and must be carried into each
change's `design.md`:

- **Issuance/entry architecture: Web2.** Account-bound tickets; entry credential =
  an **in-app dynamic QR backed by a server-signed short-TTL token** (cross-platform,
  app-controlled, not OS-shareable), validated by **signature + freshness then an
  online atomic duplicate-check** at admit (camera scan, no NFC hardware). **OS
  Wallet passes are a deferred convenience tier** (not the MVP credential — Apple
  has no self-serve rotating barcode → iOS static; OS passes are shareable → weaker
  anti-scalp; issuing them is a 個情法 §28 越境移転 to Apple/Google). Passkey is the
  **account login** identity — **NOT** a gate-time re-auth (a gate-time passkey
  step-up was explored and **rejected**; see the anti-scalp decision below). No
  blockchain. (Base recorded in `product-design.md`.)
- **Anti-scalp is a TIERED platform model, not a gate re-auth (settled after
  the ⑥ step-up exploration).** Layers, lightest→heaviest: (1) **account passkey**
  login (phishing-resistant); (2) **JPKI eKYC (マイナンバーカード) high-assurance
  lane** binding 1 person = 1 verified account — kills bulk/industrial scalping
  (what 不正転売禁止法 targets); JPKI certs only (never the 個人番号 → outside 番号法;
  via a 認定PF事業者, no self-certification); a **lane, not mandatory** (card
  penetration ~81% + drop-off → fallback required); a **new backlog change**;
  (3) **signed short-TTL credential + online atomic dedup** (signature/TTL defeats
  forgery/screenshot; dedup resolves the concurrent-admit race);
  (4) **official resale (⑦)** demand valve; (5) **per-event 顔認証/ID at entry**
  (`face-auth-entry`) — the ONLY layer that closes the 1:1 device-transfer /
  "escort" hand-off, for top-demand shows. **Rejected: gate-time passkey step-up**
  — WebAuthn proves phishing-resistance, **not anti-collusion**, so it cannot stop
  a holder handing over an unlocked device/pass; it only dents an already
  non-scaling residual at a disproportionate UX/auth-server cost. The strong-control
  budget goes to (5), not a gate re-auth.
- **Seller entity: `Organizer` — a role, not a company category** (name
  chosen over "Partner", which in platform contexts usually means an
  integration/affiliate partner). The Organizer is the account authorized
  to publish an artist's events and sell their tickets. It is the
  `schema.org/Event` `organizer` property, used by Eventbrite / Peatix /
  ZAIKO, and is a **distinct entity from Artist/Performer** (Ticketmaster
  splits Promoter↔Attraction; schema.org splits
  `organizer`/`performer`/`seller`). Relationship:

  ```
  Organizer (1) ──publishes──▶ (N) Event ──features──▶ (N) Artist   (existing event_performers)
       └──────── represents ──────────▶ (N) Artist                 (each artist ≤1 organizer)
  ```

  In MVP the Organizer role is filled by a vetted party: an **artist**
  self-publishing, or an **organization authorized to represent the
  artist — a record label, management/agency, or promoter**. Industry
  note: concerts are frequently organized by the promoter/management, not
  the record label per se, so the entity is defined by *authority over an
  artist's events*, not company type. "レコード会社" and "レーベル" are
  treated as interchangeable; a company owning multiple label brands is
  still one Organizer (label brand is a later display attribute). An
  artist who self-publishes is modeled as an Organizer account associated
  with that Artist, not a second entity type. An Organizer **exists only
  via admin vetting** (existence = vetted); there is no separate `verified`
  flag (a lifecycle/status can be added later if suspension is ever needed).
  An Organizer is simply associated with the artists it represents (no
  full/partial mandate concept — keep it simple), and **each artist is
  represented by at most one Organizer**.

- **Organizers: vetted only.** Reuse the existing admin approval
  pattern to onboard them. Open self-serve submission is out of scope,
  which also removes the fake-event risk.
- **Sales method: lottery only for MVP.** FCFS, common inventory pool,
  seat maps, manual draw, and preference ordering are all deferred until
  demand is proven. Lottery draws against a fixed capacity *after*
  applications close, which removes the hardest correctness problem
  (real-time oversell prevention) from the MVP.
- **Tickets per application: variable, per-event.** The organizer sets a
  `max_tickets_per_application` on each lottery phase (sized to venue
  capacity). Capacity is accounted in **tickets**, not applications.
- **Companion group entry = same-time entry (in MVP); NO open
  distribution URL.** Group attendance is handled by the lead buyer
  holding all won tickets on their own device, with the lead and
  companions entering the gate **together** (plan-1.md's "一括表示・同時
  入場", ZAIKO-style). We deliberately **reject the open 分配URL pattern**
  (each companion gets an individually shareable QR): though framed as
  free distribution, it is a scalping loophole — a scalper can win, send
  the share URL, and collect a high price **off-platform** while the
  system only sees a free hand-off. Same-time entry defeats this because a
  stranger cannot enter without the lead physically present, which does
  not scale. Backstops: signed short-TTL credential + online atomic dedup (a sold
  screenshot is stale / admits at most once) and covered-ticket legality
  (off-platform purchases are invalid at entry). **Note:** if OS Wallet passes are
  later added (convenience tier), the OS can share/transfer them outside our
  control — that
  residual is the same non-scaling 1:1 hand-off, **accepted** here and closed for
  top-demand shows by the per-event `face-auth-entry` tier (not by a gate re-auth,
  which can't close it). Residual risk (small-scale physical escort) is
  accepted. Separate-time companion entry, if ever needed, is solved later
  by **pre-registered** named companions (not an open URL) — see Open
  Decisions. The cannot-attend case is handled by official resale, not by
  companion hand-off.
- **Cannot-attend → official face-value resale, not ad-hoc refunds.** The
  buyer's own seat is account/identity-bound and cannot be handed to a
  named person; the sanctioned path is an **anonymous face-value resale
  pool** that refunds the original buyer when it sells. General refunds
  are reserved for **event cancellation**. In a lottery, the **losers
  form the natural demand pool** that absorbs returned tickets (DICE
  waitlist model). This is the anti-scalp gold standard (ローチケ/ぴあ)
  and the legally favored path. **Open timing decision:** official resale
  is listed in Phase 2, but "the buyer got sick" is a real day-one need —
  decide whether a minimal return-to-pool/resale ships in MVP or
  immediately after (see Open Decisions).
- **Legal "covered ticket" (チケット不正転売禁止法).** To make anti-scalp
  actually enforceable, tickets must (1) state on their face that resale
  without consent is prohibited, (2) specify date/venue and
  seat-or-eligible-person, (3) capture **本人確認** (purchaser name +
  contact). Ties to the ④ identity requirement and ⑥ ticket rendering.
- **First-party data supersedes; organizer-represented artists are excluded
  from scraping.** When an organizer-published event or issued ticket
  exists it supersedes the inferred/self-reported data for the same
  subject (a published event overrides the scraped
  `staged_concert`/`sales_phase`; issuing a ticket syncs the user's
  `ticket-journey` to `PAID`). Once an artist is represented by an
  Organizer (which exists only via admin vetting), that artist is simply
  **excluded from concert-search scraping** (first-party is authoritative;
  saves cost).
- **Payments: Stripe Connect, platform-intermediated, card-only MVP.**
  Liverty collects, takes a fee, pays out the organizer. **Card-only** for
  MVP (incl. debit/prepaid + Apple/Google Pay; konbini/PayPay deferred).
  The lottery charges **only winners** — via **`SetupIntent` (save card at
  application, charge winners at the draw), NOT an authorization hold**
  (holds tie up credit across parallel applications and break on
  prepaid/debit; this matches the JP norm). The domain Order/Payment entity
  is **provider- and method-agnostic** (see D2). Full design + legal scheme
  (収納代行, Organizer = seller-of-record) + counsel flags:
  [`payments-design.md`](./payments-design.md) (issue #778).
- **Web First, No Native App** (product constraint): the check-in tool is
  a PWA using the web camera, not a native scanner app.
- **Organizer identity & RBAC: Zitadel B2B org-per-tenant.** Each Organizer
  is its own Zitadel Organization; a shared, actor-named `organizer-console`
  project (owned by the `liverty-music` org) is Project-Granted to each; the
  backend authorizes from the org-scoped role claim; per-tenant orgs are
  created at runtime via the Management API from admin vetting. Full model
  and rationale: [`zitadel-tenancy-model.md`](./zitadel-tenancy-model.md).

## MVP Decomposition

Six numbered steps, dependency-ordered — each independently reviewable and
releasable. Step ① (organizer platform) is itself decomposed into four
sub-changes (see its row and `organizer-platform-design.md`).

```
① organizer platform  (decomposed into 4 sub-changes — see organizer-platform-design.md)
     organizer-tenancy ─▶ organizer-accounts ─┬─▶ organizer-console
                                               └─▶ organizer-rpc-server
     │
     ├──▶ ② organizer-event-authoring   (event page create / publish / private URL)
     │         │
     │         ├──▶ ③ follower-event-publish-notification   ★ ships early, no ticketing needed
     │         │
     │         └──▶ ④ lottery-application   (lottery phase, apply, auto draw, win/loss, 本人確認)
     │                    │
     │                    └──▶ ⑤ ticket-purchase-and-issuance   (Stripe → order → issued ticket)
     │                                 │
     │                                 └──▶ ⑥ ticket-wallet-and-checkin   (wallet + OS Wallet/rotating-barcode + online atomic dedup + check-in PWA)
```

| # | Change | Adds (capabilities / entities) | Depends on | Boundary rationale |
|---|--------|--------------------------------|------------|--------------------|
| ① | **organizer platform** (4 sub-changes) | The vetted-seller foundation, split to keep each change reviewable: **`organizer-tenancy`** (identity-management topology delta + Zitadel platform IaC: `organizer-console` project/roles/apps + provisioner machine user + per-org passkey login), **`organizer-accounts`** (Organizer entity + admin vetting RPCs + runtime tenant-provisioning saga + operator bootstrap + `deactivated` hook + analytics), **`organizer-console`** (`organizer.html` entry + hosting `organizer.{base}` + runtime-config delta), **`organizer-rpc-server`** (dedicated `api.organizer.{base}` server + CORS + `OrganizerService.Get` + org-scoped authz). Full design + resolved gap-audit: [`organizer-platform-design.md`](./organizer-platform-design.md). | existing admin only | A completeness audit showed a single change hid ~33 gaps (a dedicated API server, dedicated hosting, provisioning saga, offboarding). Splitting by surface (identity/accounts/console/rpc-server) mirrors the admin precedent and keeps each spec complete. |
| ② | `organizer-event-authoring` | Organizer-authored Event/Series/Venue, publish flow, **private visibility via signed tokenized URL**, first-party supersedes scraped concerts, **organizer-represented artists excluded from scraping** | ① | Turns the existing `Series/Event/Venue/event_performers` model from a scrape-reconstruction target into a first-party authoring target. |
| ③ | `follower-event-publish-notification` — **largely absorbed by ②** | ② `Publish` emits `CONCERT.created`, which the **existing `notify-concert` consumer already turns into follower push** (verified in code). So ③ is mostly delivered for free by ②. **Re-scoped to at most a thin change** (organizer-specific message copy / deeplink; UNLISTED/DRAFT never notify is handled in ②) and may be dropped. | ② | Confirmed during ② design: `CONCERT.created` → `NotifyNewConcerts` already notifies artist followers, so a separate publish→notify build is redundant. |
| ④ | `lottery-application` | LotterySalesPhase (**first-party; distinct from the scraped `sales_phase`, no merge**), `max_tickets_per_application`, TicketApplication, automatic draw, win/loss, payment deadline (owned by ④), **本人確認 identity + 1 account / 1 application** | ② | Draw logic is substantial and stands alone. Couples to payment only through "winning = right to purchase". 本人確認 also makes tickets legally "covered". Organizer sets phase capacity (no venue-capacity field exists upstream). |
| ⑤ | `ticket-purchase-and-issuance` | Order (provider/method-agnostic, opaque payment refs), platform-intermediated Stripe payment (card/wallet/**konbini async**), **Web2 account-bound Ticket issuance** (N per order), event-cancellation refund, `ticket-journey` sync to PAID | ④ | Stripe integration is heavy on its own: post-win payment → order → issuance is a single pipeline. |
| ⑥ | `ticket-wallet-and-checkin` | Ticket wallet UI (renders the **covered-ticket face**), **in-app dynamic QR = server-signed short-TTL token**, **signature+freshness then online atomic duplicate-check** at admit, **same-time group entry**, **reception PWA (web-camera, no NFC)**, entry status | ⑤ | Requires an issued ticket. App-first credential (cross-platform, not OS-shareable). **No gate-time passkey step-up** (rejected). **OS Wallet passes, NFC tap, offline scanning, per-event 顔認証 are deferred (future).** PWA honors No-Native-App. |

### Recommended sequencing note

①② introduce most of the new proto entities — land them first to
stabilize the schema. ④⑤ then finalize LotterySalesPhase/Order/Ticket. ③
carries minimal proto change (reuses existing notification), so it can
start right after ② merges and delivers value fastest.

## Phase 2+ Backlog

Deferred until demand is proven. Each becomes its own `/opsx:propose`
change when picked up:

- `official-resale` — anonymous face-value resale pool (the sanctioned
  cannot-attend / anti-scalp path; reuses lottery losers as the demand
  pool). **Calibration (market-design-notes #2): PULL EARLY — now a market
  default** (post-チケトレ, resale moved in-platform) and the cannot-attend
  valve → plan it **immediately after the lottery/ticketing MVP (⑥)**, not
  deep in Phase 2. Full design (money model = refund-seller + fresh-sale, no
  individual payee; legal must-haves; lifecycle; counsel brief):
  [`resale-design.md`](./resale-design.md).
- `face-auth-entry` — the **per-event high-assurance entry tier** on top of ⑥'s
  signed-credential + online-dedup base: **photo-bound tickets →
  live-face-match-to-open** (hardware-free, on-device). This is the anti-scalp
  layer that **actually closes the 1:1 device-transfer / escort hand-off** (which
  a gate-time passkey step-up cannot — see the Guiding anti-scalp decision), so it
  is where the "strong control" budget goes for top-demand shows. Enabled
  per-event (not universal). **⚠️ Privacy: face-feature templates are 個人識別符号
  and, under the 令和8年 個情法改正, a new 特定生体情報 category (mandatory pre-notice,
  strengthened 利用停止/消去 rights, opt-out-provision ban) — NOT 要配慮個人情報.**
  This change MUST design purpose-notice, consent, retention/deletion, and 委託先
  監督 (vendor, e.g. Playground/MOALA) — not a one-liner. Calibration
  (market-design-notes #3): leaders' bar moved here (チケプラ 2025-12,
  デジタル庁×Playground PoC = zero resale with face auth); without it we look a
  generation behind.
- `identity-ekyc-jpki` — **JPKI eKYC (マイナンバーカード) high-assurance account
  lane**: bind 1 person = 1 verified account to kill bulk/industrial scalping.
  Uses **公的個人認証 (JPKI) certificates only — never the 個人番号** (stays outside
  番号法), via a **認定プラットフォーム事業者** (e.g. TRUSTDOCK) so no self-certification;
  ticketing is not a 犯収法 特定事業者 so a lightweight JPKI binding is proportionate
  (犯収法-grade not required). **⚠️ "Outside 番号法" ≠ light footprint:** the
  **基本4情報 (氏名/住所/性別/生年月日) + cert serial** returned from the 署名用電子証明書
  are **fully 個情法 personal data** (利用目的特定・取得通知・安全管理・保持最小化); the
  persistent serial is a linkage key → retain only for the verification purpose. A
  **lane, not mandatory** (card penetration ~81% + drop-off → non-card fallback
  required). Feeds the tiered anti-scalp model.
- `organizer-rbac-subowners` — full 4-role model (editor / viewer /
  reception staff), sub-owner invites, **audit log** (add audit subjects
  to the existing JetStream analytics pipeline).
- `first-come-inventory-pool` — FCFS + common inventory pool with
  oversell prevention (row locks / reservation TTL). Only after lottery
  validates demand.
- `seat-map-assignment` — seat map upload, block/individual seat
  assignment.
- `manual-lottery-and-preferences` — manual win/loss, 1st–3rd preference,
  supply-demand adjustment rules.
- `companion-pre-registration` — separate-time companion entry via
  pre-registered named accounts (not an open URL), if convenience demands
  it.
- `cross-sell-merch-cart` — merch cross-sell cart + venue-pickup
  fulfillment.
- `digital-content-delivery` — paid digital content delivery (signed
  URLs, entitlement control).
- `organizer-crm-segment-messaging` — segmented messaging with
  attachments.
- `organizer-realtime-dashboard` — sales visualization, demographic
  dashboard.

## Cross-cutting Design Decisions (provisional)

Recorded here so they are not lost; each is formalized (or superseded) in
the relevant change's `design.md`.

- **D1 — Lottery charges after winning.** No charge at application.
  Stripe authorization holds are too short-lived for lottery windows;
  present winners a payment deadline instead (matches the existing
  `payment_deadline_at` model and Japanese lottery UX).
- **D2 — Payment entity is provider- and method-agnostic.** Stripe
  intermediates (platform collects, takes a fee, pays out organizers).
  Apple Pay / Google Pay are **not** distinct methods — they settle as
  `card` with a `card.wallet.type` facet, so they need no dedicated
  fields. Store the stable set and nothing card/wallet-shaped as identity:

  - **Store:** `provider` (stripe), `payment_intent_id` (`pi_…`),
    `payment_method_id` (`pm_…`), `payment_method_type`
    (card/konbini/paypay/bank_transfer), own `status` enum
    (pending/awaiting_payment/paid/failed/refunded), `amount`+`currency`,
    `paid_at`. Optional nullable display facets: `wallet_type`,
    `card_brand`, `card_last4`.
  - **Do not store:** PAN/CVC/expiry/`dynamic_last4`/`fingerprint`,
    Stripe's raw status (map into our enum), or `apple_pay`/`google_pay`
    as a top-level type (would force a proto-breaking change later).
  - **Architecture (not just config):** **konbini is asynchronous** —
    the Order needs an `awaiting_payment` state and must treat
    `payment_intent.succeeded` **webhooks** (idempotent) as the source of
    truth, not the client confirm. **Apple Pay needs per-domain
    verification** (`/.well-known/apple-developer-merchantid-domain-association`)
    — the PWA service worker must not intercept `/.well-known/`. Audit
    timestamps use domain-specific `*_at` names (repo schema-lint bans
    generic `created_at/updated_at`).

- **D3 — Private events use signed tokenized URLs, not referrer control.**
  Referrer restriction is fragile (browsers strip referrers; asking
  external sites to add `<meta name="referrer">` is unrealistic) (②).
- **D4 — Check-in is a PWA + web-camera QR** (No-Native-App constraint),
  with a non-camera "tap stamp" fallback (⑥).
- **D5 — Organizer vetting reuses the existing admin console** (admin
  approves/creates organizer accounts + sets mandate); organizers use
  `organizer.html` (a third entry point, following the proven consumer/admin
  dual-entry pattern) (①).

## Open Decisions (still to make)

- **Official-resale timing.** ~~MVP vs Phase 2~~ **Leaning EARLY** after the
  2025-2026 market check: official resale is now a JP market default (post-
  チケトレ) and the cannot-attend valve, reusing the lottery loser pool →
  plan it right after the ticketing MVP (⑥), not deep in Phase 2. See
  `market-design-notes.md` #2. Final MVP-vs-immediately-after sizing TBD.
- **Separate-time companion entry.** Whether to add pre-registered named
  companions (individual QR bound to a specific account, no open URL) for
  groups who cannot enter together. Deferred by default; revisit if
  same-time entry proves too restrictive.

## Deferred Payment Details (decide later, no proto impact)

Behind the opaque payment reference; changeable without schema breaks:
Stripe charge model (destination vs separate charges & transfers) and
merchant-of-record; **primary** payout timing (immediate vs held past the
event); platform fee rate; tax/currency (JPY tax-inclusive, インボイス);
特定商取引法 seller-of-record disclosure and refund-policy wording.

Note: the **official-resale** money decisions are now SETTLED in
[`resale-design.md`](./resale-design.md) — price is locked to 券面代金
(face-value only, no cap knob), and the reselling **seller refund is
triggered on resale completion with a short hold-back, NOT held to the
event** (ぴあ/ticket board/e+/tiget-aligned). Only the *primary* buyer→Organizer
payout timing above remains a ⑤ decision (and resale does not depend on it).

Note: merchant-of-record / 特商法 / refund policy, Stripe Connect account
type & onboarding, and the fee rate are business/legal decisions with
long lead times — start them on a separate track before ⑤ begins.

## Existing-asset Reuse Map

- **Rides on existing assets:** follow + push + notification pipeline
  (③), `Series/Event/Venue/event_performers` model (②), Zitadel org
  scoping and admin approval queue (①), JetStream analytics pipeline
  (audit log, Phase 2), `sales_phase` and `ticket-journey` models (④⑤),
  PWA infrastructure (⑥).
- **Net new:** organizer accounts, tokenized private URLs,
  lottery application/draw, Stripe integration, Order, account-bound
  ticket issuance, same-time group entry, **signed short-TTL entry-token
  issuance/validation (in-app dynamic QR)**, reception check-in PWA.

## Operating Notes

- Every change flows through the cross-repo release order: specification
  PR merge → GitHub Release → BSR gen → backend/frontend consume the new
  types.
- Create each change only when its work starts; keep this document as the
  single map of intended sequencing.
