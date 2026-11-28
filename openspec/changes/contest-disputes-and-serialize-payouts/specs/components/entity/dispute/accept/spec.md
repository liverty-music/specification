# Spec Delta

## Purpose

Concedes an Open Dispute and records it Accepted: a chargeback is conceded to the payment provider, so the disputed money stays with the cardholder; an inquiry is conceded by the refund its caller has already made.

## ADDED Requirements

### Requirement: Conceded once

Accept SHALL record the given Open Dispute Accepted with the given close time. For a chargeback it SHALL first concede it to the payment provider; for an inquiry it SHALL tell the payment provider nothing, since the caller has already refunded the payment, which resolves an inquiry. When the Dispute is already Accepted, or the payment provider reports the chargeback already conceded, Accept SHALL record it Accepted without conceding again. It SHALL fail with FailedPrecondition, changing nothing, when the Dispute is Contested, Won or Lost, or when the payment provider reports it closed with another outcome or escalated, which the caller tells apart by syncing it (Dispute.Sync); with NotFound when no Dispute has the id; and with Unavailable, recording nothing, when the payment provider cannot be reached.

#### Scenario: Open chargeback accepted
- **WHEN** Accept is called for an Open chargeback
- **THEN** the payment provider is told the platform concedes it, and the Dispute is Accepted with its close time

#### Scenario: Open inquiry accepted
- **WHEN** Accept is called for an Open inquiry whose payment was refunded
- **THEN** the Dispute is Accepted and nothing is sent to the payment provider

#### Scenario: Conceded before a lost response
- **WHEN** Accept is called again after the payment provider conceded the chargeback but the Dispute was not recorded
- **THEN** the Dispute is Accepted and nothing is conceded again

#### Scenario: Already contested
- **WHEN** Accept is called for a Contested Dispute
- **THEN** it fails with FailedPrecondition and the Dispute stays Contested

#### Scenario: Payment provider unreachable
- **WHEN** the payment provider cannot be reached
- **THEN** Accept fails with Unavailable and the Dispute stays Open
