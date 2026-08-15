## Purpose

Detect and alert on systemic Web Push delivery failure — a high delivery failure ratio, or notifications being generated while no active subscriptions can receive them — so that a push outage surfaces operationally within minutes instead of going unnoticed for weeks.

## ADDED Requirements

### Requirement: Alert on sustained push delivery failure
The system SHALL raise an operational alert when the Web Push delivery failure ratio stays above a defined threshold over a sustained window, so that a systemic inability to deliver notifications is detected without manual inspection. The alert SHALL be derived from the delivery-outcome signal emitted by the notification service and SHALL identify that push delivery is failing.

#### Scenario: Delivery failure ratio breaches threshold
- **WHEN** the ratio of `failed` to total notification deliveries stays above the configured threshold over the configured evaluation window
- **THEN** an alert SHALL fire to the operational notification channel
- **AND** the alert SHALL indicate that Web Push delivery is failing

#### Scenario: Healthy delivery does not alert
- **WHEN** notification deliveries are predominantly `delivered` over the evaluation window
- **THEN** no delivery-failure alert SHALL fire

### Requirement: Alert on active-subscription starvation
The system SHALL raise an operational alert when notifications are being generated but essentially no active push subscriptions exist to receive them (e.g., failures dominated by `no active push subscription`), so that a mass subscription loss is caught even though each individual send "completes". 

#### Scenario: Notifications generated with no deliverable subscriptions
- **WHEN** notifications are being created over the evaluation window
- **AND** deliveries fail predominantly with `no active push subscription`
- **THEN** an alert SHALL fire to the operational notification channel
- **AND** the alert SHALL indicate that push subscriptions are absent for the targeted recipients
