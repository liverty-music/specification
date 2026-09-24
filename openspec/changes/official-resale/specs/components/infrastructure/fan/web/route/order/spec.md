## Purpose

The route where a fan reviews and confirms a ticket order, showing the price and, for a resale purchase, the return policy that applies to that order before the purchase is committed.

## ADDED Requirements

### Requirement: Buyer return policy on the final confirmation screen

The system SHALL display a **返品特約 (no-return / no-cancellation clause)** to the
resale **buyer** on the **final order-confirmation screen** (the screen
immediately before the confirm-purchase action), clearly and legibly — **not only
as a link to the terms**. This is **required separately from the fee disclosure**
and satisfies 特商法 §12-6 so the default 8-day 通信販売 return right (§15-3) does
not apply. Event-cancellation refunds are a **separate** matter governed by the
ticket's cancellation policy and MUST NOT contradict this clause.

#### Scenario: Return policy shown before purchase confirmation

- **WHEN** a buyer reaches the final confirmation screen for a resale purchase
- **THEN** a clear "purchase is non-returnable / non-cancellable" clause is displayed on that screen, distinct from the fee disclosure
