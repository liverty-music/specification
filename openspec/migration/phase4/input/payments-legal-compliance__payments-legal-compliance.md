<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: Livemode launch gate

The platform SHALL NOT process livemode (real-money) ticket payments until all of the following are in place: a 収納代行 counsel opinion covering the discharge clause (弁済免責), hold-to-event escrow, and no cross-border remittance; 適格請求書発行事業者 registration with a decided 媒介者交付特例 stance; and the consumer-disclosure, receipt, and data-transfer obligations below. Until then paid ticketing runs in Stripe **test mode** only.

#### Scenario: Livemode blocked until obligations met

- **WHEN** paid ticketing would be switched to livemode
- **THEN** the switch is withheld unless the 収納代行 opinion, 適格請求書発行事業者 registration, and the consumer/receipt/data-transfer disclosures below are all satisfied

#### Scenario: Test mode requires no gate

- **WHEN** paid ticketing runs in Stripe test mode
- **THEN** no real money moves and the launch gate does not apply

<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: Total-price display (総額表示)

All consumer-facing prices SHALL be shown as a tax-inclusive (税込) amount, and any order with multiple line items SHALL show tax-inclusive line amounts plus a tax-inclusive grand total.

#### Scenario: Consumer sees tax-inclusive total

- **WHEN** a fan views a ticket price or an order summary anywhere in the purchase/apply/confirmation flow
- **THEN** the displayed amount is tax-inclusive (税込) and, for multi-line orders, a tax-inclusive grand total is shown

<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: 特定商取引法 final confirmation

Before a purchase is committed, the platform SHALL present a final-confirmation screen (最終確認画面) that states the return/refund policy (返品特約: no returns except event cancellation/postponement per the ⑤ refund taxonomy) and the responsible business's information (事業者情報) for the applicable Organizer.

#### Scenario: Final confirmation before commit

- **WHEN** a fan reaches the last step before their payment is committed
- **THEN** they see the 返品特約 (cancellation/postponement-only refunds) and the per-Organizer 事業者情報, and must pass this screen to complete the purchase

<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: PCI SAQ A — no PAN handling

The platform SHALL NOT receive, transmit, or store raw card numbers (PAN); card entry SHALL be delegated to Stripe-hosted fields (Elements), keeping the integration within PCI SAQ A scope, with EMV 3DS available on the card flow.

#### Scenario: Card data never touches the platform

- **WHEN** a fan enters card details
- **THEN** the PAN is captured only by Stripe-hosted fields and never reaches or is persisted by the platform, and only non-PAN facets (brand, last4) are retained

<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: Receipts and qualified invoices (適格請求書)

Receipts and invoices issued for ticket payments SHALL carry the qualified-invoice registration number (登録番号) and the credit-card-payment notation (クレカ決済表記) required by the インボイス制度, consistent with the chosen 媒介者交付特例 stance.

#### Scenario: Issued receipt is invoice-compliant

- **WHEN** a receipt or invoice is issued for a ticket payment
- **THEN** it includes the 登録番号 and the クレカ決済 notation required for input-tax-credit eligibility

<!-- change: payments-legal-compliance | old_cap: payments-legal-compliance -->
### Requirement: Cross-border data-transfer disclosure and retention

The platform's privacy disclosure SHALL state that personal data is entrusted to Stripe (US) as a cross-border transfer (個人情報 越境移転) and SHALL be backed by an executed DPA; payment records SHALL be retained per 電子帳簿保存法.

#### Scenario: Privacy disclosure covers the Stripe US transfer

- **WHEN** a fan reviews the privacy policy before paying
- **THEN** the Stripe (US) 越境移転 委託 is disclosed, a DPA is in place, and payment records are retained per 電子帳簿保存法

