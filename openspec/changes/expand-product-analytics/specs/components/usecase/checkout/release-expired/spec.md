## ADDED Requirements

### Requirement: Each expired checkout is reported

When ReleaseExpired ends a Checkout because its hold lapsed, it SHALL send a "checkout expired" signal for product analytics for the Checkout's fan, carrying the Checkout, its TicketType and the ticket count. A Checkout ended for another reason SHALL NOT send this signal. A failure to send it SHALL NOT change the release.

#### Scenario: Hold lapsed
- **WHEN** a Checkout's hold lapses before the fan pays
- **THEN** one checkout-expired signal is sent for that fan
