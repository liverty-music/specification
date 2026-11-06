## ADDED Requirements

### Requirement: Each fan with a Paid Order is told of the cancellation and of the refund

When a member cancels an Event with SeriesUseCase.Cancel, each fan with a Paid Order of it SHALL receive a cancellation email and push saying the concert is 中止 (cancelled) and its tickets are refunded. When an admin then refunds the Order for 中止, that fan SHALL receive a refund email and push with the amount and the card it went to. Each fan SHALL receive each notice once per Order.

#### Scenario: Cancelled and refunded
- **WHEN** a member cancels an Event with two Paid Orders of two fans, and an admin uses `Refund all` on the Artist concerts screen
- **THEN** each fan receives one cancellation email and push, then one refund email and push with their amount

#### Scenario: Deleted right after the refunds
- **WHEN** an admin uses `Delete` after `Refund all` and the refund notices were already sent
- **THEN** each fan still has the refund email, and the Event no longer exists
