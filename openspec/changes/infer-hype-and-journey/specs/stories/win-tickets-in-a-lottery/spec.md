## ADDED Requirements

### Requirement: An entry marks the fan's journey Applied

When a fan's lottery entry is made, TicketJourneyUseCase.MarkApplied SHALL record the fan's ticket journey for the event as Applied, set by the platform, after the entry is announced, so the Dashboard and the event detail sheet show Applied without the fan setting it. Recording the journey SHALL never fail or delay the entry. A winning fan's journey then becomes Paid as the purchase is recorded.

#### Scenario: Entry made

- **WHEN** a fan with no journey for the event confirms their entry
- **THEN** the Dashboard and the event detail sheet show Applied for the event

#### Scenario: Entry wins

- **WHEN** the fan's entry wins and the purchase is recorded
- **THEN** the fan's journey for the event is Paid
