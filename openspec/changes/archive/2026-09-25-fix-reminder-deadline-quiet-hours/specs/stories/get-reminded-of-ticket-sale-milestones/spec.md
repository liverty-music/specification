# Spec Delta

## MODIFIED Requirements

### Requirement: No reminder at night

A milestone that falls between 22:00 and 08:00 in the fan's time zone SHALL be reminded at 08:00, or, for a closing reminder whose deadline comes before 08:00, at 21:00 the evening before — one hour before the quiet window begins, so the reminder's own due time never falls during quiet hours.

#### Scenario: Opening at 02:00

- **WHEN** a tracked presale opens at 02:00 in the fan's time zone
- **THEN** the fan's Ticket Sales Open push arrives at about 08:00
