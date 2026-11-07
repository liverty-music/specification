# components/entity/order/send-refund-email Specification

## Purpose
Emails the user of a Refunded Order how much was refunded to their card for the Order's 中止 (cancelled) concert and that the refunded tickets are no longer valid.

## Requirements

### Requirement: SendRefundEmail tells the user the refund was made

SendRefundEmail SHALL take an Order, an email address and a finished message, and SHALL send one email to that address. It SHALL fail with InvalidArgument when the address or the message is empty, and with Unavailable when email cannot be sent. It records nothing on the Order.

#### Scenario: Email sent
- **WHEN** SendRefundEmail runs for a Refunded Order with an address and a message
- **THEN** one email with that message reaches the address

#### Scenario: Message missing
- **WHEN** SendRefundEmail runs with an empty message
- **THEN** it fails with InvalidArgument and nothing is sent

#### Scenario: Address missing
- **WHEN** SendRefundEmail runs with an empty address
- **THEN** it fails with InvalidArgument and nothing is sent

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendRefundEmail fails with Unavailable
