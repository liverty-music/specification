# components/entity/organizer/set-platform-fee-rate Specification

## Purpose
Stores the platform fee rate applied to an Organizer's future Orders.

## Requirements

### Requirement: Rate stored for future orders

SetPlatformFeeRate SHALL store the given rate as the Organizer's platform fee rate. It SHALL fail with InvalidArgument when the rate is outside 0 to 30%, and with NotFound when no Organizer has the id.

#### Scenario: Pilot rate

- **WHEN** an admin sets an Organizer's rate to 5%
- **THEN** the Organizer's rate is 5%

#### Scenario: Out of range

- **WHEN** the rate is 31%
- **THEN** SetPlatformFeeRate fails with InvalidArgument and nothing changes
