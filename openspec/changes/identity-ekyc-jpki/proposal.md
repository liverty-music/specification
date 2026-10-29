## Why

The tiered anti-scalp model (roadmap Guiding Decision) needs its **heavy lever**:
bind **1 account = 1 verified real person** so bulk/industrial scalping (bot
armies, one-person-many-accounts) is structurally resisted. Account passkey +
signed-credential + dedup (⑥) only defeat forgery/screenshots and double-entry;
they do not stop a scalper opening 100 accounts. **Account identity verification is what caps that.**

This is a **business anti-scalp measure — it is NOT required by チケット不正転売禁止法**
(which targets 業としての定価超譲渡; even entry 本人確認 is only an 努力義務). And it is
**not, by itself, an anti-resale mechanism**: it stops many-accounts, but a verified
fan can still resell/lend a ticket — closing that needs the separate per-event
gate 顔認証 (`face-auth-entry`). The gold-standard JP method is **マイナンバーカード
公的個人認証 (JPKI)**; the vendor is **Pocket Sign (PocketSign Verify)**, a 主務大臣認定
プラットフォーム事業者. Grounding: the merged roadmap decision + the session's JPKI +
Pocket Sign research (デジタル庁×Playground PoC: identity verification **+ face** entry → zero resale
vs ~300 on paper). Companion to
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- Introduce an **`IdentityVerification`** (the result of a fan's 本人確認) via **JPKI using
  Pocket Sign** — because our client is a **PWA**, the fan reads their マイナンバーカード
  (**physical NFC or スマホJPKI**) in the **PocketSign app** (installed separately) via
  **PocketSign Stamp** (our backend opens a Stamp session and the app returns the
  signed result, which the backend validates through Stamp's Verify backend), and we
  **delete the raw certificate promptly**. Only JPKI data — **never the 個人番号**
  (outside 番号法). We ride on Pocket Sign's 認定 as a 加盟事業者 (no own 主務大臣認定).
  <!-- Corrected 2026-09-02: earlier drafts said "Verify SDK embedded in our app";
       a PWA uses Stamp + the PocketSign app instead. The デジタル認証アプリ is a
       separate, unused path. See design.md "MVP scope & corrections". -->
- **1 person = 1 verified account (anti-scalp core).** Identify the person by the
  **provider user ID** (`provider_user_id`: the verification provider's ID for the User,
  Pocket Sign's `User.userId`, a **tenant-scoped ID** stable across card
  renewal/re-issue/cert-type) — **store only this ID** (never the serial, never the
  個人番号) — and enforce **≤1 Active IdentityVerification per `provider_user_id`**;
  expose a **per-person limit** that ④/⑤ enforce across accounts sharing it. Because it is tenant-scoped,
  cross-platform detection is out of scope.
- **A lane, NOT mandatory.** A fan is unverified until they hold an Active
  IdentityVerification. A **TicketSale MAY require verification** (Verified-any or
  JPKI-only). **MVP is JPKI-only** — a
  verification-required event admits only fans with a My Number Card. A **運転免許証 IC fallback**
  (Pocket Sign's separate **Verify CardInfo**) for non-card fans is **POST-MVP**
  (deferred 2026-09-02): it proves identity but yields **no equivalent stable
  per-person dedupe key** (weaker dedupe), so it does not advance the anti-scalp core and
  is not worth the extra product integration for the MVP. The 任意/平等 fairness of a
  JPKI-only requirement is a legal-review item. (Proto keeps the fallback enums for
  forward-compat.)
- **現況確認 for freshness.** Periodically re-check revocation / 基本4情報 change /
  expiry via Pocket Sign 現況確認 and prompt re-verification (not a hard lock).
- **Privacy by design.** "Outside 番号法" ≠ light 個情法 footprint: specify 利用目的
  (verification + anti-scalp dedup), 取得通知, 安全管理, **store only `provider_user_id`** (基本4情報
  only if a use case justifies it), honor JPKI 目的外利用禁止 (every check is logged/
  reported to J-LIS), and a **deletion** policy.

Scope guardrails (MVP): **JPKI-only** via Pocket Sign (client path = **Stamp + the
PocketSign app**) as the high-assurance method; **lane, not mandatory**; account-level,
consumed by ④/⑤ as a "verified person + per-person limit" signal, storing **only
`provider_user_id`**. **POST-MVP:** the 運転免許証 (Verify CardInfo) fallback and verified-name
(基本4情報 via 署名用証明書 + Consent) binding. **Not** a 犯収法 obligor flow (ticketing is
not a 特定事業者) — lightweight JPKI binding, not 取引時確認; and **not required by
チケット不正転売禁止法** (④'s self-declared 本人確認 satisfies the 特定興行入場券 requirement).

## Capabilities

### New Capabilities

- `components/usecase/identity-verification/create`: JPKI account verification via the verification provider
- `components/usecase/identity-verification/recheck`: 現況確認 (revocation / attribute-change re-check)

### Modified Capabilities

<!-- ④ lottery entry (LotteryEntryUseCase.AuthorizeCard since enter-lottery-at-confirm) consumes the verified-person +
     per-person-limit signal (its per-account limit becomes per verified person where
     a TicketSale requires verification) and ⑤ checkout gates on an Active
     IdentityVerification; the enforcement hooks are folded into ④/⑤ when this lands.
     identity-management provides the underlying Zitadel account. Post-MVP, where a
     sale requires verification, the IdentityVerification's verified name becomes
     authoritative for the covered-ticket 本人確認 (ticket face). See design.md.
     usecase/ticket-sale/set-verification-requirement was added by unify-ticket-sales
     (archived 2026-10-12). The lottery gate is on usecase/lottery-entry/authorize-card
     since enter-lottery-at-confirm (archived 2026-10-27) removed Start; its deltas are
     written on the TicketStock model of remodel-ticket-sales, which archives first. -->
- `components/entity/identity-verification`: Verified-person dedupe via the provider user ID; Per-person limit signal and mixed populations; Privacy — data minimization and deletion
- `components/usecase/ticket-sale/set-verification-requirement`: Only マイナンバーカード verification satisfies a requirement
- `components/usecase/lottery-entry/authorize-card`: Verification adds no verified name (moved from `lottery-entry/start`, which enter-lottery-at-confirm removes)
- `components/infrastructure/fan/web/route/lottery-entry`: An unverified fan is asked to verify before entering
- `components/infrastructure/fan/web/route/settings`: the identity verification result (success, or the reason for a failure) is shown on Settings

## Impact

- **Depends on:** `identity-management` (the Zitadel account) + **Pocket Sign
  (PocketSign Stamp on Verify)**. The **MVP ships on the free sandbox (mock env)
  in every environment, including prod** — no upfront cost. The **加盟契約 (¥300k
  init + per-verify fees, ~2-3mo integration) is POST-MVP**, needed only to flip
  to the production 認定PF endpoint after the MVP is proven (see design.md "MVP
  scope & corrections"). Counsel review of the Pocket Sign 利用規約 + data flow
  (task 0.2) still precedes handling real cards.
- **Feeds:** ④ lottery entry (per-verified-person limit), ⑤ checkout and ticket
  issuance (verification gate + covered-ticket 本人確認),
  and the tiered anti-scalp model. Complements ⑥'s per-scan controls, ⑦ resale.
- **New entities:** `IdentityVerification` (user_id, method JPKI/licence,
  `provider_user_id`, dedupe_strength STRONG/WEAK, verify_time, status) and a per-sale
  **verification requirement** (None / Verified-any / JPKI-only). A client treats an
  Active IdentityVerification as verified (no separate account verification level).
- **New RPCs:** `IdentityVerificationService.Start` / `Create` (via the provider's
  session), `Recheck` (現況確認), `Get()`; organizer
  `TicketSaleService.SetVerificationRequirement`.
- **Legal/privacy:** JPKI only (outside 番号法, never 個人番号/serial); 個情法
  利用目的/最小保持(provider_user_id のみ)/削除; JPKI 目的外利用禁止 + J-LIS logging; 犯収法 not an
  obligor; fallback prevents non-card exclusion (substantively equivalent).
- **Not in scope:** 顔認証 entry (`face-auth-entry`); 犯収法 取引時確認; 券面事項
  (マイナンバー/顔写真) read.
