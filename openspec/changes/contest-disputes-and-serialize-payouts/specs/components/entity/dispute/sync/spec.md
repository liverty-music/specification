# Spec Delta

## Purpose

Records a dispute as the payment provider reports it now, so notices that arrive late, twice or out of order leave the Dispute in the provider's latest state without moving it backwards.

## ADDED Requirements

### Requirement: Recorded from the payment provider's current state

Sync SHALL take an Order and a provider dispute ID, read the dispute from the payment provider, and store or update the Dispute with it: whether it is an inquiry, the reason, the amount, the evidence due time, the open time and the status the provider reports, returning the Dispute. A dispute not yet stored SHALL be stored with the provider's status. An update SHALL only move forward: an inquiry becomes a chargeback, not back, and an escalation makes a Contested inquiry Open with the chargeback's evidence due time; a provider outcome closes an Open or Contested Dispute as Won or Lost with its close time. An Accepted Dispute SHALL stay Accepted whatever the provider reports. It SHALL fail with FailedPrecondition, changing nothing, when the provider reports Won for a Dispute recorded Lost, or Lost for one recorded Won; with NotFound when no Order has the id or the provider has no such dispute; and with Unavailable when the payment provider cannot be reached.

#### Scenario: New dispute recorded
- **WHEN** Sync is called for a Paid Order with a provider dispute ID no Dispute has, which the provider reports awaiting a response
- **THEN** an Open Dispute with the provider's reason, amount, evidence due time and open time is stored and returned

#### Scenario: Notice delivered again
- **WHEN** Sync is called for a Contested Dispute that the provider still reports under review
- **THEN** nothing changes and the Contested Dispute is returned

#### Scenario: Escalation seen before the inquiry was stored
- **WHEN** Sync is called for a provider dispute no Dispute has, which started as an inquiry and is now a chargeback
- **THEN** an Open Dispute that is not an inquiry is stored with the chargeback's evidence due time

#### Scenario: Contested inquiry escalates
- **WHEN** Sync is called for a Contested inquiry that the provider now reports as a chargeback awaiting a response
- **THEN** the Dispute is Open, no longer an inquiry, with the chargeback's evidence due time

#### Scenario: Outcome reported
- **WHEN** Sync is called for a Contested Dispute that the provider reports won
- **THEN** the Dispute is Won with its close time

#### Scenario: Accepted dispute reported closed
- **WHEN** Sync is called for an Accepted Dispute that the provider reports lost or closed
- **THEN** nothing changes and the Dispute stays Accepted

#### Scenario: Lost dispute reported won
- **WHEN** Sync is called for a Lost Dispute that the provider reports won
- **THEN** it fails with FailedPrecondition and the Dispute stays Lost

#### Scenario: Second dispute on the same payment
- **WHEN** Sync is called for an Order that has a Lost Dispute, with another provider dispute ID
- **THEN** a second Dispute is stored for the Order
