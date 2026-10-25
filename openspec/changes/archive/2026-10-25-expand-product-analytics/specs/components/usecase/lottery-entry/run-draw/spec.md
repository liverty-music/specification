## ADDED Requirements

### Requirement: Each entry's result is reported

After RunDraw records an entry Won or Lost, it SHALL send a "lottery result" signal for product analytics for the entry's fan, carrying the TicketSale, the TicketType, the result, for a loss whether it came from a failed capture, and the time of the draw as the time it happened. A failure to send it SHALL NOT change the draw.

#### Scenario: Two entries, one place
- **WHEN** RunDraw admits one of two entries for a TicketType with quantity 1
- **THEN** one Won signal and one Lost signal are sent, each for its entry's fan
