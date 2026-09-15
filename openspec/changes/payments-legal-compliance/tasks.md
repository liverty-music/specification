## 1. Legal / tax opinions & registrations (external, long-lead)

- [ ] 1.1 収納代行 counsel opinion (#778 flag 1): confirm the discharge clause (弁済免責) + hold-to-event escrow + no cross-border remittance structure under 資金決済法 (Stripe Connect onboarding execution is owned by `ticket-settlement-and-payout`).
- [ ] 1.2 適格請求書発行事業者 registration with the 税務署; decide the 媒介者交付特例 stance (platform issues qualified invoices on behalf of Organizers vs. Organizer self-issues) — this decision gates the receipt content in §3.
- [ ] 1.3 Stripe live 審査 (account activation for livemode) — prerequisite to lifting the launch gate.

## 2. Consumer-facing compliance UI + copy

- [ ] 2.1 総額表示: tax-inclusive (税込) line amounts + tax-inclusive grand total on ALL consumer-facing prices (④ apply/checkout + ⑤ Order surfaces). Owns the obligation; the pixels land in ④/⑤.
- [ ] 2.2 特商法 最終確認画面: final pre-commit confirmation showing 返品特約 (no returns except cancellation/postponement per ⑤'s refund taxonomy) + per-Organizer 事業者情報.
- [ ] 2.3 PCI SAQ A: verify card entry is Stripe Elements only (no PAN reaches the platform); EMV 3DS available on the card flow; SAQ A attestation on file.

## 3. Records, receipts & data-transfer disclosures

- [ ] 3.1 領収書 / 適格請求書: issued receipts/invoices carry the 登録番号 + クレカ決済表記 per インボイス制度, consistent with the §1.2 媒介者交付特例 decision.
- [ ] 3.2 個人情報 越境移転: privacy disclosure of the Stripe (US) 委託 cross-border transfer + executed DPA.
- [ ] 3.3 電子帳簿保存法: payment-record retention conforms to 電子帳簿保存法.

## 4. Launch gate

- [ ] 4.1 Confirm all of §1–§3 are satisfied, then lift the livemode launch gate (flip paid ticketing from Stripe test mode to livemode). Until then paid ticketing runs in test mode only.
