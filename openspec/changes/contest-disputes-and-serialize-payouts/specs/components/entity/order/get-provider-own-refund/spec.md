# Spec Delta

## Purpose

Finds the refund the payment provider made for an Order's own refund (a 中止 refund or an accepted inquiry), told apart from resale refunds of the same payment, including one made but not yet recorded on the Order.

## ADDED Requirements

### Requirement: The Order's own refund at the payment provider

GetProviderOwnRefund SHALL return the refund the payment provider made from the Order's captured payment as the Order's own refund, with its provider refund ID, amount and time, or report that there is none; refunds made for resale listings of the Order's Tickets SHALL NOT count. It SHALL fail with FailedPrecondition when the Order has no captured payment, with NotFound when no Order has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Cancellation refund made, not recorded
- **WHEN** a 10000 yen Order's own refund of 10000 yen was made at the payment provider and the Order is still Paid
- **THEN** that refund is returned with its amount 10000

#### Scenario: Only a resale refund
- **WHEN** the only refund from the Order's payment was made for a resale listing of one of its Tickets
- **THEN** GetProviderOwnRefund reports no own refund
