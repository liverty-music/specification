# Spec Delta

## ADDED Requirements

### Requirement: The editor creates a named lottery sale for one event

The editor SHALL create a Lottery TicketSale for the event it was opened from, with a name, the window, and one TicketType for that event with a quantity, a per-account limit and a price. The name SHALL be required, and the per-account limit SHALL default to 4 and accept 1 to 10. When a sale of the event already overlaps the entered window, the screen SHALL say so next to the window and SHALL not save.

#### Scenario: Presale for one event
- **WHEN** an operator names the sale ファンクラブ先行, keeps the 10-day window and enters 100 tickets at 8000 yen
- **THEN** a Lottery sale named ファンクラブ先行 is created with one TicketType of 100 tickets at 8000 yen and a per-account limit of 4

#### Scenario: Missing name
- **WHEN** the operator saves without a name
- **THEN** an error is shown next to the name and nothing is saved

#### Scenario: Overlapping window
- **WHEN** the event already has a sale from 1 to 10 November and the operator enters a window starting 8 November
- **THEN** the screen says the window overlaps that sale and nothing is saved
