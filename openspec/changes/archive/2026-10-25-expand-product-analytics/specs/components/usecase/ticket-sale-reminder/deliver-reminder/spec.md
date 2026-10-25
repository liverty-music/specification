## ADDED Requirements

### Requirement: The reminder names its milestone

The sales_reminder notification that DeliverReminder issues SHALL carry, in its message data, the TicketSale and the milestone the reminder is for, so that the fan's reaction can be told apart by milestone.

#### Scenario: Apply-close reminder
- **WHEN** DeliverReminder runs for the apply-close milestone of a sale
- **THEN** the issued notification's data names that sale and the apply-close milestone
