## ADDED Requirements

### Requirement: Card numbers never reach the platform

The platform SHALL NOT receive, transmit, or store raw card numbers (PAN); card entry SHALL happen in the payment processor's hosted card fields, keeping the platform within PCI SAQ A scope, with 3-D Secure available on the card flow.

#### Scenario: Card data never touches the platform

- **WHEN** a fan enters card details
- **THEN** the PAN is captured only by the payment processor's hosted card fields and never reaches or is persisted by the platform, and only non-PAN facets (brand, last4) are retained

### Requirement: An Order's receipt is a qualified invoice (適格請求書)

Receipts and invoices issued for ticket payments SHALL carry the qualified-invoice registration number (登録番号) and the credit-card-payment notation (クレカ決済表記) required by the インボイス制度, consistent with the chosen 媒介者交付特例 stance.

#### Scenario: Issued receipt is invoice-compliant

- **WHEN** a receipt or invoice is issued for a ticket payment
- **THEN** it includes the 登録番号 and the クレカ決済 notation required for input-tax-credit eligibility
