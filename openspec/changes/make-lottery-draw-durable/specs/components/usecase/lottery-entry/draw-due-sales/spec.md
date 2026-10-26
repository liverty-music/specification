## MODIFIED Requirements

### Requirement: Draw within one minute after the window closes

DrawDueSales SHALL run every 1 minute. It SHALL list the sales due at the current time with TicketSale.ListDueForDraw and run LotteryEntryUseCase.Draw for each. A sale whose draw fails or stops SHALL NOT stop the others and stays due, so its draw resumes on a later run and keeps what it already recorded. When the listing fails, DrawDueSales SHALL fail with that error and draw nothing.

#### Scenario: Window closes
- **WHEN** a Lottery sale's end time passes
- **THEN** the sale is drawn within 1 minute

#### Scenario: Window still open
- **WHEN** a Lottery sale's end time has not passed
- **THEN** it is not drawn

#### Scenario: Drawn once
- **WHEN** a sale has been drawn
- **THEN** later runs do not draw it again

#### Scenario: One sale fails
- **WHEN** the draw of one due sale fails
- **THEN** the other due sales are still drawn and the failed sale's draw resumes within 1 minute, keeping the TicketTypes it already recorded
