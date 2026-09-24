# PushSubscription.Send

## Purpose

Hands one message to the push service of one PushSubscription, encrypted for that browser.

## Requirements

### Requirement: Send reports acceptance, a gone browser, or failure

Send SHALL deliver the message to the push service of the PushSubscription and succeed when the push service accepts it. The push service SHALL be asked to keep the message for up to 24 hours when the browser is offline. When the push service reports that the subscription no longer exists, Send SHALL fail with NotFound. Any other rejection or failure to reach the push service SHALL fail with Internal.

#### Scenario: Accepted

- **WHEN** the push service accepts the message
- **THEN** Send succeeds

#### Scenario: Browser unsubscribed

- **WHEN** the push service reports that the subscription is gone
- **THEN** Send fails with NotFound

#### Scenario: Push service error

- **WHEN** the push service rejects the message for another reason or cannot be reached
- **THEN** Send fails with Internal

#### Scenario: Keep time for an offline browser

- **WHEN** Send hands a message to the push service
- **THEN** the push service is asked to keep it for 24 hours while the browser is offline
