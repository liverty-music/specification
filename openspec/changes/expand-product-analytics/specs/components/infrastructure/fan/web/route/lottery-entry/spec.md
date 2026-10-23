## ADDED Requirements

### Requirement: Starting and submitting an entry are reported

When the screen starts the entry with LotteryEntryService.Start, it SHALL send one usage analytics event with the Event, the TicketType and the ticket count. When confirming the entry succeeds, it SHALL send one entry-submitted event with the same values.

#### Scenario: Entry submitted
- **WHEN** a fan starts an entry for 2 tickets and confirms it
- **THEN** one entry-started event and one entry-submitted event are sent, each with the count 2
