# PushSubscription.Delete

## Purpose

Removes the PushSubscription of one fan's browser, identified by the fan and the browser's push address.

## Requirements

### Requirement: Delete removes only that pair and is idempotent

Delete SHALL remove the PushSubscription with the given endpoint when it belongs to the given fan, and nothing else: the fan's other browsers and other fans' subscriptions stay. When no PushSubscription of that fan has that endpoint, Delete SHALL succeed and change nothing.

#### Scenario: One of two browsers

- **WHEN** the fan has two registered browsers and Delete runs for one endpoint
- **THEN** that PushSubscription is removed and the other remains

#### Scenario: Not registered

- **WHEN** no PushSubscription of the fan has the endpoint
- **THEN** Delete succeeds and nothing changes

#### Scenario: Another fan's address

- **WHEN** the endpoint is registered by another fan
- **THEN** Delete succeeds and that fan's PushSubscription remains

### Requirement: A removed subscription is announced with the change

When Delete removes a PushSubscription, it SHALL announce the PushSubscription as unsubscribed, carrying it as it was, together with the removal: both are stored or neither is. When Delete removes nothing, it SHALL announce nothing. When the announcement cannot be recorded, Delete SHALL fail with Unavailable and the PushSubscription SHALL remain.

#### Scenario: Registered browser removed

- **WHEN** Delete removes one of the fan's PushSubscriptions
- **THEN** one unsubscription is announced, carrying that PushSubscription

#### Scenario: Not registered

- **WHEN** no PushSubscription of the fan has the endpoint
- **THEN** Delete succeeds and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** Delete would remove a PushSubscription and the announcement cannot be recorded
- **THEN** Delete fails with Unavailable and the PushSubscription remains
