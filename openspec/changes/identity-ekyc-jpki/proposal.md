## Why

The tiered anti-scalp model (roadmap Guiding Decision) needs its **heavy lever**:
bind **1 account = 1 verified real person** so bulk/industrial scalping (bot
armies, one-person-many-accounts) is structurally resisted. Account passkey +
signed-credential + dedup (⑥) only defeat forgery/screenshots and double-entry;
they do not stop a scalper opening 100 accounts. **Account eKYC is what caps that.**

This is a **business anti-scalp measure — it is NOT required by チケット不正転売禁止法**
(which targets 業としての定価超譲渡; even entry 本人確認 is only an 努力義務). And it is
**not, by itself, an anti-resale mechanism**: it stops many-accounts, but a verified
buyer can still resell/lend a ticket — closing that needs the separate per-event
gate 顔認証 (`face-auth-entry`). The gold-standard JP method is **マイナンバーカード
公的個人認証 (JPKI)**; the vendor is **Pocket Sign (PocketSign Verify)**, a 主務大臣認定
プラットフォーム事業者. Grounding: the merged roadmap decision + the session's JPKI +
Pocket Sign research (デジタル庁×Playground PoC: eKYC **+ face** entry → zero resale
vs ~300 on paper). Companion to
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- Introduce a **`VerifiedIdentity`** account-level verification via **JPKI using
  Pocket Sign** — because our client is a **PWA**, the fan reads their マイナンバーカード
  (**physical NFC or スマホJPKI**) in the **PocketSign app** (installed separately) via
  **PocketSign Stamp** (our backend opens a Stamp session and the app returns the
  signed result, which the backend validates through Stamp's Verify backend), and we
  **delete the raw certificate promptly**. Only JPKI data — **never the 個人番号**
  (outside 番号法). We ride on Pocket Sign's 認定 as a 加盟事業者 (no own 主務大臣認定).
  <!-- Corrected 2026-09-02: earlier drafts said "Verify SDK embedded in our app";
       a PWA uses Stamp + the PocketSign app instead. The デジタル認証アプリ is a
       separate, unused path. See design.md "MVP scope & corrections". -->
- **1 person = 1 verified account (anti-scalp core).** Use Pocket Sign's **`User.id`**
  (a **tenant-scoped UUID**, stable across card renewal/re-issue/cert-type) as the
  person key — **store only this UUID** (never the serial, never the 個人番号) — and
  enforce **≤1 active verified account per `User.id`**; expose a **per-person
  limit** that ④/⑤ enforce across accounts sharing it. Because it is tenant-scoped,
  cross-platform detection is out of scope.
- **A lane, NOT mandatory.** Default `UNVERIFIED`; verification → `IDENTITY_VERIFIED`.
  An **event/phase MAY require a verified identity**. **MVP is JPKI-only** — a
  verification-required event admits only card-holders. A **運転免許証 IC fallback**
  (Pocket Sign's separate **Verify CardInfo**) for non-card fans is **POST-MVP**
  (deferred 2026-09-02): it proves identity but yields **no equivalent stable
  per-person key** (weaker dedupe), so it does not advance the anti-scalp core and
  is not worth the extra product integration for the MVP. The 任意/平等 fairness of a
  JPKI-only requirement is a legal-review item. (Proto keeps the fallback enums for
  forward-compat.)
- **現況確認 for freshness.** Periodically re-check revocation / 基本4情報 change /
  expiry via Pocket Sign 現況確認 and prompt re-verification (not a hard lock).
- **Privacy by design.** "Outside 番号法" ≠ light 個情法 footprint: specify 利用目的
  (verification + anti-scalp dedup), 取得通知, 安全管理, **store only `User.id`** (基本4情報
  only if a use case justifies it), honor JPKI 目的外利用禁止 (every check is logged/
  reported to J-LIS), and a **deletion** policy.

Scope guardrails (MVP): **JPKI-only** via Pocket Sign (client path = **Stamp + the
PocketSign app**) as the high-assurance method; **lane, not mandatory**; account-level,
consumed by ④/⑤ as a "verified person + per-person limit" signal, storing **only
`User.id`**. **POST-MVP:** the 運転免許証 (Verify CardInfo) fallback and verified-name
(基本4情報 via 署名用証明書 + Consent) binding. **Not** a 犯収法 obligor flow (ticketing is
not a 特定事業者) — lightweight JPKI binding, not 取引時確認; and **not required by
チケット不正転売禁止法** (④'s self-declared 本人確認 satisfies the 特定興行入場券 requirement).

## Capabilities

### New Capabilities
- `identity-ekyc`: JPKI account verification via **Pocket Sign (Verify SDK + API)**,
  the `VerifiedIdentity` entity + account verification level, the 1-person-1-account
  dedupe on Pocket Sign **`User.id`** + per-person limit signal, 現況確認 freshness,
  the per-event "requires verified identity" flag with a 運転免許証 fallback (weaker
  dedupe), and the privacy (利用目的 / store-only-User.id / 削除) requirements.

### Modified Capabilities
<!-- None specced as a delta here. ④ lottery-application consumes the verified-person
     + per-person-limit signal (its "1 account / 1 application" becomes "1 verified
     person / 1 application" where an event requires verification) and ⑤ consumes
     the verification level; those enforcement hooks are folded into ④/⑤ when this
     lands. identity-management provides the underlying Zitadel account. Where an
     event requires verification, the verified identity is authoritative for the
     covered-ticket 本人確認 (⑤/④ face content). See design.md. -->

## Impact

- **Depends on:** `identity-management` (the Zitadel account) + **Pocket Sign
  (PocketSign Verify)** — 加盟契約, Verify SDK/API, ¥300k init + per-verify fees,
  ~2-3mo integration; free sandbox for PoC. Counsel review of the Pocket Sign
  利用規約 + data flow.
- **Feeds:** ④ `lottery-application` (per-verified-person limit), ⑤
  `ticket-purchase-and-issuance` (verification level + covered-ticket identity),
  and the tiered anti-scalp model. Complements ⑥'s per-scan controls, ⑦ resale.
- **New entities:** `VerifiedIdentity` (account_ref, method JPKI/licence,
  `pocket_sign_user_id`, dedupe_strength STRONG/WEAK, verified_at, status), account
  **verification level**, a per-event **requires-verified-identity** flag.
- **New RPCs:** start/complete Verify (challenge–response), 現況確認 re-check,
  get-my-verification-status; admin/organizer set per-event requirement.
- **Legal/privacy:** JPKI only (outside 番号法, never 個人番号/serial); 個情法
  利用目的/最小保持(User.id のみ)/削除; JPKI 目的外利用禁止 + J-LIS logging; 犯収法 not an
  obligor; fallback prevents non-card exclusion (substantively equivalent).
- **Not in scope:** 顔認証 entry (`face-auth-entry`); 犯収法 取引時確認; 券面事項
  (マイナンバー/顔写真) read.
