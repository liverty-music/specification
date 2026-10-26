## Purpose

Records that a Lottery TicketSale's draw completed, so the sale is no longer due for a draw.

## ADDED Requirements

### Requirement: The draw time is recorded once

RecordDraw SHALL set a Lottery TicketSale's draw time to the given time when it has none. When the sale already has a draw time, it SHALL succeed and keep that time. It SHALL fail with NotFound when no TicketSale has the id, and with FailedPrecondition when the sale's method is not Lottery.

#### Scenario: Draw recorded
- **WHEN** RecordDraw is called for a closed Lottery sale without a draw time
- **THEN** the sale has that draw time

#### Scenario: Recorded again
- **WHEN** RecordDraw is called for a sale that already has a draw time
- **THEN** it succeeds and the sale keeps the first draw time

#### Scenario: First-come sale
- **WHEN** RecordDraw is called for a FirstCome sale
- **THEN** it fails with FailedPrecondition and nothing changes
