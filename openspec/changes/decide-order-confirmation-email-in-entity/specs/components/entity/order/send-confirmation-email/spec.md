## ADDED Requirements

### Requirement: The confirmation email is sent as given
SendConfirmationEmail SHALL take an Order's id, the email address of the Order's user and the finished message, and send the message as an email to that address, tagged with the Order's id. Whether the email is due, and recording that it was sent, are the caller's (Order.ConfirmationEmailDue, Order.MarkConfirmationSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: Email sent
- **WHEN** SendConfirmationEmail is called with an address and a message
- **THEN** one email with the message is sent to the address

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendConfirmationEmail fails with Unavailable

## REMOVED Requirements

### Requirement: One confirmation email per order

**Reason**: The mail adapter decided whether the email was due and recorded the send. The adapter now only sends; the decision is the entity's and the record the usecase's.
**Migration**: Order.ConfirmationEmailDue decides whether the email is due and the notification usecase records the send (Order.MarkConfirmationSent); its scenarios "Redelivered event" and "Mail unavailable" are covered by usecase/notification/send-order-confirmation ("Order announced twice", "Mail unavailable"). An Order that does not exist fails with NotFound at the usecase's Order.Get, no longer at SendConfirmationEmail.
