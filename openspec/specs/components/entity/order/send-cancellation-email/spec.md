# components/entity/order/send-cancellation-email Specification

## Purpose
Emails the user of an Order that the Order's concert is 中止 (cancelled) and that the price of the tickets they still hold is refunded to the card they paid with.

## Requirements

### Requirement: SendCancellationEmail tells the user the concert is cancelled

SendCancellationEmail SHALL take an Order, an email address and a finished message, and SHALL send one email to that address. It SHALL fail with InvalidArgument when the address or the message is empty, and with Unavailable when email cannot be sent. It records nothing on the Order.

#### Scenario: Email sent
- **WHEN** SendCancellationEmail runs for an Order with an address and a message
- **THEN** one email with that message reaches the address

#### Scenario: Address missing
- **WHEN** SendCancellationEmail runs with an empty address
- **THEN** it fails with InvalidArgument and nothing is sent

#### Scenario: Message missing
- **WHEN** SendCancellationEmail runs with an empty message
- **THEN** it fails with InvalidArgument and nothing is sent

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendCancellationEmail fails with Unavailable
