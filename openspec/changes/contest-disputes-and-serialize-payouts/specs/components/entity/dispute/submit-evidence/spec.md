# Spec Delta

## Purpose

Hands the platform's evidence for an Open Dispute to the payment provider for the card issuer to rule on, and records the Dispute Contested.

## ADDED Requirements

### Requirement: Evidence submitted once

SubmitEvidence SHALL take an Open Dispute and its evidence: the Order's purchase (pay time, amount, ticket count, the Event's name, local date and Venue), the account the Tickets are bound to and its email address when the account still exists, each Ticket with its issue time and, when admitted, its admit time and Scanner, the refund terms, and every refund already made from the Order's payment (the Order's own refund and each resale refund) with its amount and time. It SHALL submit them to the payment provider as final, within the provider's limit of 150000 characters for all text, and record the Dispute Contested with the given submit time. When the Dispute is already Contested, or the payment provider reports evidence already submitted for it, SubmitEvidence SHALL record it Contested without submitting again. It SHALL fail with FailedPrecondition, recording nothing, when the Dispute is Accepted, Won or Lost, when the payment provider reports the dispute closed or escalated, or when it refuses evidence because the dispute cannot be contested; the caller tells these apart by syncing the Dispute (Dispute.Sync), which shows a closure or an escalation; with NotFound when no Dispute has the id; and with Unavailable, recording nothing, when the payment provider cannot be reached.

#### Scenario: Evidence submitted
- **WHEN** SubmitEvidence is called for an Open Dispute with the purchase, the account, two Tickets of which one was admitted, the refund terms and no refund
- **THEN** the evidence is submitted and the Dispute is Contested with its submit time

#### Scenario: Submitted before a lost response
- **WHEN** SubmitEvidence is called again after the payment provider took the evidence but the Dispute was not recorded
- **THEN** the Dispute is Contested and nothing is submitted again

#### Scenario: Dispute that cannot be contested
- **WHEN** the payment provider refuses evidence because the dispute cannot be contested
- **THEN** SubmitEvidence fails with FailedPrecondition and the Dispute stays Open

#### Scenario: Closed at the payment provider
- **WHEN** the payment provider reports the dispute already closed
- **THEN** SubmitEvidence fails with FailedPrecondition and nothing is recorded

#### Scenario: Payment provider unreachable
- **WHEN** the payment provider cannot be reached
- **THEN** SubmitEvidence fails with Unavailable and the Dispute stays Open
