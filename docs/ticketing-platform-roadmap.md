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

- **Issuance/entry architecture: Web2.** Account-bound tickets +
  server-signed rotating QR + Passkey identity. No blockchain. (Already
  recorded in `product-design.md`.)
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
  not scale. Backstops: rotating QR + login (a sold screenshot is
  useless) and covered-ticket legality (off-platform purchases are
  invalid at entry). Residual risk (small-scale physical escort) is
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
     │                                 └──▶ ⑥ ticket-wallet-and-checkin   (wallet + same-time entry + rotating QR + check-in PWA)
```

| # | Change | Adds (capabilities / entities) | Depends on | Boundary rationale |
|---|--------|--------------------------------|------------|--------------------|
| ① | **organizer platform** (4 sub-changes) | The vetted-seller foundation, split to keep each change reviewable: **`organizer-tenancy`** (identity-management topology delta + Zitadel platform IaC: `organizer-console` project/roles/apps + provisioner machine user + per-org passkey login), **`organizer-accounts`** (Organizer entity + admin vetting RPCs + runtime tenant-provisioning saga + operator bootstrap + `deactivated` hook + analytics), **`organizer-console`** (`organizer.html` entry + hosting `organizer.{base}` + runtime-config delta), **`organizer-rpc-server`** (dedicated `api.organizer.{base}` server + CORS + `OrganizerService.Get` + org-scoped authz). Full design + resolved gap-audit: [`organizer-platform-design.md`](./organizer-platform-design.md). | existing admin only | A completeness audit showed a single change hid ~33 gaps (a dedicated API server, dedicated hosting, provisioning saga, offboarding). Splitting by surface (identity/accounts/console/rpc-server) mirrors the admin precedent and keeps each spec complete. |
| ② | `organizer-event-authoring` | Organizer-authored Event/Series/Venue, publish flow, **private visibility via signed tokenized URL**, first-party supersedes scraped concerts, **organizer-represented artists excluded from scraping** | ① | Turns the existing `Series/Event/Venue/event_performers` model from a scrape-reconstruction target into a first-party authoring target. |
| ③ | `follower-event-publish-notification` — **largely absorbed by ②** | ② `Publish` emits `CONCERT.created`, which the **existing `notify-concert` consumer already turns into follower push** (verified in code). So ③ is mostly delivered for free by ②. **Re-scoped to at most a thin change** (organizer-specific message copy / deeplink; UNLISTED/DRAFT never notify is handled in ②) and may be dropped. | ② | Confirmed during ② design: `CONCERT.created` → `NotifyNewConcerts` already notifies artist followers, so a separate publish→notify build is redundant. |
| ④ | `lottery-application` | LotterySalesPhase (extends `sales_phase`), `max_tickets_per_application`, TicketApplication, automatic draw, win/loss, payment deadline, **本人確認 identity + 1 account / 1 application** | ② | Draw logic is substantial and stands alone. Couples to payment only through "winning = right to purchase". 本人確認 also makes tickets legally "covered". |
| ⑤ | `ticket-purchase-and-issuance` | Order (provider/method-agnostic, opaque payment refs), platform-intermediated Stripe payment (card/wallet/**konbini async**), **Web2 account-bound Ticket issuance** (N per order), event-cancellation refund, `ticket-journey` sync to PAID | ④ | Stripe integration is heavy on its own: post-win payment → order → issuance is a single pipeline. |
| ⑥ | `ticket-wallet-and-checkin` | Ticket wallet UI, **same-time group entry (all tickets on lead's device)**, **server-signed rotating QR + Passkey re-auth**, **reception PWA (web-camera QR via getUserMedia)**, real-time entry status | ⑤ | Requires an issued ticket. Same-time entry is how a multi-ticket win is used (no distribution); check-in as a PWA honors No-Native-App. |

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
- `face-auth-entry` — anti-scalp **identity tier** on top of ⑥'s rotating-QR
  + Passkey floor: **photo-bound tickets → live-face-match-to-open**
  (hardware-free, on-device), with **マイナンバーカード** as an opt-in
  high-assurance option. Calibration (market-design-notes #3): the leaders'
  bar moved here (チケプラ 2025-12); without it we look a generation behind.
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
  ticket issuance, same-time group entry, rotating-QR signing, reception
  check-in PWA.

## Operating Notes

- Every change flows through the cross-repo release order: specification
  PR merge → GitHub Release → BSR gen → backend/frontend consume the new
  types.
- Create each change only when its work starts; keep this document as the
  single map of intended sequencing.
