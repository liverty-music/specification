## ADDED Requirements

### Requirement: Each admitted ticket is reported

For each Ticket that Admit admits, it SHALL send a "ticket admitted" signal for product analytics for the Ticket's fan, carrying the Ticket, its Event and its admit time as the time it happened. A rejected scan SHALL NOT send this signal. A failure to send it SHALL NOT change the admission.

#### Scenario: Two tickets admitted in one scan
- **WHEN** a scan admits 2 Tickets of one fan
- **THEN** two ticket-admitted signals are sent for that fan
