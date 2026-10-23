## ADDED Requirements

### Requirement: Checkout steps and the purchase start are reported

Each time the checkout shows one of its steps (count, personal details, payment, final confirmation, done, outcome, or the verification notice), it SHALL send one usage analytics event naming the step, with the Event and the TicketType. When continuing from the count step starts holding the tickets, it SHALL send one purchase-initiated event with the Event, the TicketType, the ticket count and the price band of the TicketType.

#### Scenario: Fan reaches the final confirmation
- **WHEN** a fan holds 2 tickets, enters personal details and authorizes the card
- **THEN** one purchase-initiated event and one step event each for personal details, payment and final confirmation are sent

#### Scenario: Unverified fan on a verified sale
- **WHEN** the checkout shows the verification notice instead of starting
- **THEN** one step event naming the verification notice is sent and no purchase-initiated event is sent
