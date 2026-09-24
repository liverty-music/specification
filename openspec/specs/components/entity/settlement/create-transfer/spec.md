# Settlement.CreateTransfer

## Purpose

Pays one Organizer's net share of one captured charge out of the platform balance to the Organizer's payout account.

## Requirements

### Requirement: Funds are held until the transfer

Captured ticket money SHALL stay on the platform balance, held under the 収納代行 (collection agency) scheme, until CreateTransfer runs for it; CreateTransfer SHALL move the Organizer's net share of that one charge to the Organizer's payout account, tied to that charge, and the platform fee SHALL be the part not transferred. CreateTransfer SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Net share is transferred

- **WHEN** CreateTransfer runs for a captured charge with a positive net share
- **THEN** the net share reaches the Organizer's payout account, tied to that charge, and the platform fee stays on the platform balance

#### Scenario: Funds before the transfer

- **WHEN** a charge is captured and CreateTransfer has not run for it
- **THEN** all of the charge stays on the platform balance

#### Scenario: Non-positive amount

- **WHEN** CreateTransfer is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and nothing is transferred
