# Spec Delta

## MODIFIED Requirements

### Requirement: One confirmation email per order

SendConfirmationEmail SHALL take an Order, the email address of the Order's user and the finished message. When the Order has no confirmation send time, it SHALL send the message as an email to that address and then set the Order's confirmation send time. When the time is already set, it SHALL send nothing and succeed. A failure between sending and recording can lead to a second email on retry; no other case sends twice. It SHALL fail with InvalidArgument when the address or the message is empty, with Unavailable when email cannot be sent, and with NotFound when no Order has the id.

#### Scenario: Email sent

- **WHEN** SendConfirmationEmail is called for an Order without a confirmation send time
- **THEN** one email with the message is sent to the user's address and the confirmation send time is set

#### Scenario: Redelivered event

- **WHEN** SendConfirmationEmail is called again for an Order with a confirmation send time
- **THEN** it succeeds and no email is sent

#### Scenario: Mail unavailable

- **WHEN** email cannot be sent
- **THEN** SendConfirmationEmail fails with Unavailable and the confirmation send time stays unset
