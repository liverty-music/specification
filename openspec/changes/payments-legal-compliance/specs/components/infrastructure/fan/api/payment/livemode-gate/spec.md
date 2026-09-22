## Purpose

Gates whether the platform may process real-money ticket payments, keeping ticketing confined to a no-money-at-stake mode until the legal counsel, tax registration, and disclosure obligations for live payments are all satisfied.

## ADDED Requirements

### Requirement: Livemode launch gate

The platform SHALL NOT process livemode (real-money) ticket payments until all of the following are in place: a 収納代行 counsel opinion covering the discharge clause (弁済免責), hold-to-event escrow, and no cross-border remittance; 適格請求書発行事業者 registration with a decided 媒介者交付特例 stance; and the consumer-disclosure, receipt, and data-transfer obligations below. Until then paid ticketing runs in Stripe **test mode** only.

#### Scenario: Livemode blocked until obligations met

- **WHEN** paid ticketing would be switched to livemode
- **THEN** the switch is withheld unless the 収納代行 opinion, 適格請求書発行事業者 registration, and the consumer/receipt/data-transfer disclosures below are all satisfied

#### Scenario: Test mode requires no gate

- **WHEN** paid ticketing runs in Stripe test mode
- **THEN** no real money moves and the launch gate does not apply
