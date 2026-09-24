# PushSubscription.Get

## Purpose

Returns the PushSubscription of one fan's browser, identified by the fan and the browser's push address.

## Requirements

### Requirement: Get returns the fan's subscription for that address or NotFound

Get SHALL return the PushSubscription with the given endpoint when it belongs to the given fan. When no PushSubscription of that fan has that endpoint, including when the endpoint belongs to another fan, Get SHALL fail with NotFound.

#### Scenario: Registered browser

- **WHEN** Get runs with a fan and one of that fan's endpoints
- **THEN** that PushSubscription is returned

#### Scenario: Unknown address

- **WHEN** no PushSubscription has the endpoint
- **THEN** Get fails with NotFound

#### Scenario: Another fan's address

- **WHEN** the endpoint is registered by another fan
- **THEN** Get fails with NotFound
