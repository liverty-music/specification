<!-- merge_group: ISSUANCE | target: components/usecase/ticket/issue-from-captured-win | members: 1 -->

<!-- member: ticket-purchase-and-issuance | flags:  -->
### Requirement: Idempotent issuance

**Capture** and its provider webhooks belong to ④; **refund/dispute** provider
webhooks and their idempotency belong to **`ticket-settlement-and-payout`** (which
makes the refund calls). ⑤ SHALL make **issuance idempotent**: replaying the
Won-captured signal (or retrying issuance) MUST NOT double-issue tickets or
double-create an Order for the same application.

#### Scenario: Replayed captured-win signal issues exactly once

- **WHEN** ④'s Won-captured signal for an application is observed/retried more than once
- **THEN** the Order is created once and tickets are issued exactly once

