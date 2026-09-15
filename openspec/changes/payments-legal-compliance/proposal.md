## Why

Paid ticketing (roadmap ⑤ `ticket-purchase-and-issuance`) is implemented and verified in Stripe **test mode**, but flipping it to **livemode (real money)** is gated by Japanese legal, tax, and payments-compliance obligations that are external, long-lead, and mostly not code. Tracking them inside ⑤ blocks ⑤ from archiving on its own implementation. This change **carves those go-live obligations into their own capability** so ⑤ can archive independently, and the launch gate has a single, auditable home.

## What Changes

- **Move** the launch-gating legal/tax/compliance items out of `ticket-purchase-and-issuance` (its tasks §0.1, §0.2 and §6.1–§6.4) into this capability. ⑤ keeps only its spec/implementation tasks.
- Establish the **payments-compliance obligations** the platform must satisfy before charging real money:
  - **収納代行 counsel opinion** (資金決済法): discharge clause (弁済免責) + hold-to-event escrow + no cross-border. (Stripe Connect onboarding execution is owned by `ticket-settlement-and-payout`.)
  - **適格請求書発行事業者 registration** + 媒介者交付特例 stance (インボイス制度).
  - **総額表示** (税込 lines + grand total) on all consumer-facing prices.
  - **特商法 最終確認画面** + 返品特約 (no returns except cancellation/postponement) + per-Organizer 事業者情報.
  - **PCI SAQ A** (Stripe Elements, no PAN) + EMV 3DS attestation.
  - **個人情報 越境移転** (Stripe US 委託) privacy disclosure + DPA; 電子帳簿保存法 record retention; 領収書/適格請求書 (クレカ決済表記, 登録番号).
- No new proto/RPC surface. A few items have consumer-facing UI surfaces (総額表示, 特商法 最終確認画面) that partly live in ④'s apply/checkout and ⑤'s Order views.

## Capabilities

### New Capabilities
- `payments-legal-compliance`: the legal, tax, and payments-compliance obligations that gate flipping paid ticketing to livemode — counsel opinions, tax registrations, consumer-facing 総額表示 / 特商法 disclosures, PCI SAQ A, and 越境移転 / record-retention / receipt (適格請求書) obligations.

### Modified Capabilities
<!-- None. ⑤'s delta spec requirements do not change: the moved items were tracking
     tasks (§0/§6), not spec-level requirements of ticket-purchase-and-issuance. -->

## Impact

- **Provider**: decided — Stripe Connect (test mode now; live launch deferred behind this gate).
- **Cross-capability**: 収納代行 escrow/payout execution is `ticket-settlement-and-payout`; the checkout/apply UI that carries 総額表示 + 特商法 最終確認 spans ④ (`lottery-application`) and ⑤ (`ticket-purchase-and-issuance`) surfaces — this capability owns the obligations, those changes own the pixels.
- **External**: legal counsel (#778), 税務署 適格請求書発行事業者 registration, Stripe live 審査, DPA execution — none block ⑤'s spec/implementation or archive.
- **No code/proto surface** introduced by this capability itself; it is a launch-gate tracking + obligations spec.
