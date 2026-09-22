## Purpose

Keeps raw card numbers from ever reaching or being stored by the platform by delegating card entry to the payment processor's own hosted fields, so the platform's card-data handling stays within the lightest compliance scope available.

## ADDED Requirements

### Requirement: PCI SAQ A — no PAN handling

The platform SHALL NOT receive, transmit, or store raw card numbers (PAN); card entry SHALL be delegated to Stripe-hosted fields (Elements), keeping the integration within PCI SAQ A scope, with EMV 3DS available on the card flow.

#### Scenario: Card data never touches the platform

- **WHEN** a fan enters card details
- **THEN** the PAN is captured only by Stripe-hosted fields and never reaches or is persisted by the platform, and only non-PAN facets (brand, last4) are retained
