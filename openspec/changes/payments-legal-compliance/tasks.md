## 1. Legal / tax opinions & registrations (external, long-lead)

- [ ] 1.1 収納代行 counsel opinion (#778 flag 1): confirm the discharge clause (弁済免責) + hold-to-event escrow + no cross-border remittance structure under 資金決済法 (Stripe Connect onboarding execution is owned by `ticket-settlement-and-payout`). The same opinion covers official resale (`official-resale` design D4–D7): the two money legs (a partial refund of the listing fan's own payment and a new sale to the purchasing fan, so money never moves between fans), the 10% resale fee framed as 役務の対価, and whether the platform needs its own 特定商取引法に基づく表記 page for that fee.
- [ ] 1.2 適格請求書発行事業者 registration with the 税務署; decide the 媒介者交付特例 stance (platform issues qualified invoices on behalf of Organizers vs. Organizer self-issues) — this decision gates the receipt content in §3.
- [ ] 1.3 Stripe live 審査 (account activation for livemode) — prerequisite to lifting the launch gate.

## 2. Consumer-facing compliance UI + copy

- [x] 2.1 総額表示: tax-inclusive (税込) line amounts + tax-inclusive grand total on all consumer-facing prices of the first-come purchase. Shipped by `first-come-ticket-sales` (archived 2026-10-11): `components/infrastructure/fan/web/route/checkout` "Choose the count and hold the tickets" (price per ticket and total 税込), `route/event` "Ticket section shows the sale" (price 税込) and `usecase/notification/send-order-confirmation` (total 税込). The lottery entry screen is not used for the pilot and is left to the change that brings the lottery to real money.
- [x] 2.2 特商法 最終確認画面: final pre-commit confirmation showing 返品特約 (no returns except event cancellation 中止) + per-Organizer 事業者情報. Shipped by `first-come-ticket-sales`: `components/infrastructure/fan/web/route/checkout` "特商法 final confirmation" (every item incl. the Organizer's business details, the no-cancellation and no-cooling-off statement and the way back to correct).
- [ ] 2.3 PCI SAQ A: verify card entry is Stripe Elements only (no PAN reaches the platform); EMV 3DS available on the card flow; SAQ A attestation on file.
- [ ] 2.4 Counsel reviews the consumer-facing wording before the livemode gate: the checkout's final confirmation, the confirmation email, the Terms of Service purchase article (§3.4) and the official resale article and listing screen of `official-resale`; record the outcome and any copy changes here.

## 3. Records, receipts & data-transfer disclosures

- [ ] 3.1 領収書 / 適格請求書: issued receipts/invoices carry the 登録番号 + クレカ決済表記 per インボイス制度, consistent with the §1.2 媒介者交付特例 decision. Product work: the platform issues no receipt today (no receipt in the backend or the fan app as of 2026-10-20); once §1.2 is decided, propose the receipt surface as its own change or add its tasks here.
- [ ] 3.2 個人情報 越境移転: the Privacy Policy names Stripe (US) as the payment processor entrusted with personal data, as a cross-border transfer, + executed DPA. Today section 6 only says some external services handle data on servers in the US or UK; verify the fan app's Privacy Policy text after the change.
- [ ] 3.3 電子帳簿保存法: payment-record retention conforms to 電子帳簿保存法.
- [ ] 3.4 Terms of Service ticket purchase article (`components/infrastructure/fan/web/global/legal-document` "Terms of Service state the ticket purchase terms"): add it in ja and en in the fan app; verify a unit test for "Purchase article present". The Terms have no article on ticket purchases today (sections 第1条–第9条 as of 2026-10-20).

## 4. Launch gate

- [ ] 4.1 Confirm all of §1–§3 are satisfied, and that `official-resale` and `organizer-antisocial-vetting` are shipped to production (liverty-music/specification#1074), then lift the livemode launch gate (flip paid ticketing from Stripe test mode to livemode: the fan app's `stripePublishableKey` in `k8s/namespaces/frontend/overlays/prod/fan-web-configmap.yaml` and the Pulumi config `stripeSecretKey` and `stripeWebhookSigningSecret` of the prod stack, which reach fan-api through Secret Manager). Until then paid ticketing runs in test mode only.
