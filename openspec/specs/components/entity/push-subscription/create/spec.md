# PushSubscription.Create

## Purpose

Registers a browser's push subscription for a fan, or refreshes it when that browser's push address is already registered.

## Requirements

### Requirement: Create registers each push address once

Create SHALL store a PushSubscription for the fan with the given endpoint and keys. When a PushSubscription with the same endpoint already exists, Create SHALL update it in place instead of adding a second one: its keys are replaced, its owner becomes the given fan, and its id is kept. Create SHALL return the stored PushSubscription, carrying the id it is stored under.

#### Scenario: New browser

- **WHEN** Create runs with an endpoint that is not registered
- **THEN** a PushSubscription with a new id is stored and returned

#### Scenario: Same browser registers again

- **WHEN** Create runs with an endpoint that is already registered by the same fan, with new keys
- **THEN** the existing PushSubscription's keys are replaced and it is returned with its existing id

#### Scenario: Browser moves to another fan

- **WHEN** Create runs for fan B with an endpoint registered by fan A
- **THEN** the PushSubscription now belongs to fan B and fan A no longer has it
