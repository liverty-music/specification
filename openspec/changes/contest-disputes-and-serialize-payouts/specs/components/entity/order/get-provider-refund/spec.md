# Spec Delta

## Purpose

Finds the refund the payment provider made from an Order's payment for one purpose (the Order's own refund, or the refund of one accepted inquiry), including one made but not yet recorded, told apart from the other refunds of the same payment.

## ADDED Requirements

### Requirement: A refund of the payment, by purpose

GetProviderRefund SHALL take an Order and a purpose, the Order's own refund (a 中止 refund) or the refund of one named Dispute, and return the refund the payment provider made from the Order's captured payment for that purpose, with its provider refund ID, amount and time, or report that there is none. Refunds made for other purposes, resale listings of the Order's Tickets included, SHALL NOT count. It SHALL fail with FailedPrecondition when the Order has no captured payment, with NotFound when no Order has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Cancellation refund made, not recorded
- **WHEN** a 10000 yen Order's own refund of 10000 yen was made at the payment provider and the Order is still Paid
- **THEN** that refund is returned for the Order's own refund, with its amount 10000

#### Scenario: Only an inquiry refund
- **WHEN** the only refund from the Order's payment was made for an accepted inquiry
- **THEN** GetProviderRefund reports no refund for the Order's own refund, and returns that refund for the inquiry's Dispute

#### Scenario: Only a resale refund
- **WHEN** the only refund from the Order's payment was made for a resale listing of one of its Tickets
- **THEN** GetProviderRefund reports no refund for the Order's own refund
