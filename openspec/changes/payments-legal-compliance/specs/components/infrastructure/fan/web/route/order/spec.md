## Purpose

The route where a fan reviews and confirms a ticket order, showing a tax-inclusive price and the return policy and responsible business's information that apply before the purchase is committed.

## ADDED Requirements

### Requirement: Total-price display (総額表示)

All consumer-facing prices SHALL be shown as a tax-inclusive (税込) amount, and any order with multiple line items SHALL show tax-inclusive line amounts plus a tax-inclusive grand total.

#### Scenario: Consumer sees tax-inclusive total

- **WHEN** a fan views a ticket price or an order summary anywhere in the purchase/apply/confirmation flow
- **THEN** the displayed amount is tax-inclusive (税込) and, for multi-line orders, a tax-inclusive grand total is shown

### Requirement: 特定商取引法 final confirmation

Before a purchase is committed, the platform SHALL present a final-confirmation screen (最終確認画面) that states the return/refund policy (返品特約: no returns except event cancellation/postponement per the ⑤ refund taxonomy) and the responsible business's information (事業者情報) for the applicable Organizer.

#### Scenario: Final confirmation before commit

- **WHEN** a fan reaches the last step before their payment is committed
- **THEN** they see the 返品特約 (cancellation/postponement-only refunds) and the per-Organizer 事業者情報, and must pass this screen to complete the purchase
