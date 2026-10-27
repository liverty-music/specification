## MODIFIED Requirements

### Requirement: Draw within one minute after the window closes

DrawDueSales SHALL run every 1 minute. It SHALL list the sales due at the current time with TicketSale.ListDueForDraw and run LotteryEntryUseCase.Draw for each, once per sale: a sale listed again while its draw is still running, or after its draw ended with a failure, SHALL NOT be drawn a second time. A sale whose draw fails SHALL NOT stop the others. When the listing fails, DrawDueSales SHALL fail with that error and draw nothing.

#### Scenario: Window closes
- **WHEN** a Lottery sale becomes due for a draw
- **THEN** its draw starts within 1 minute

#### Scenario: Window still open
- **WHEN** a Lottery sale's end time has not passed
- **THEN** it is not drawn

#### Scenario: Drawn once
- **WHEN** a sale has been drawn, or its draw is still running when the next run lists it
- **THEN** later runs do not draw it again

#### Scenario: One sale fails
- **WHEN** the draw of one due sale ends with an unexpected error
- **THEN** the other due sales are still drawn, and the failed sale is not drawn again by later runs
