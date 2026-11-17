# components/entity/order/send-confirmation-email Specification

## Purpose
Sends the email confirming one Order to the Order's user, as the caller composed it. Whether the email is due and recording that it was sent are the caller's, so it is sent once per Order.

## Requirements

### Requirement: The confirmation email is sent as given
SendConfirmationEmail SHALL take an Order's id, the email address of the Order's user and the finished message, and send the message as an email to that address, tagged with the Order's id. Whether the email is due, and recording that it was sent, are the caller's (Order.ConfirmationEmailDue, Order.MarkConfirmationSent). It SHALL fail with InvalidArgument when the address or the message is empty and with Unavailable when email cannot be sent.

#### Scenario: Email sent
- **WHEN** SendConfirmationEmail is called with an address and a message
- **THEN** one email with the message is sent to the address

#### Scenario: Mail unavailable
- **WHEN** email cannot be sent
- **THEN** SendConfirmationEmail fails with Unavailable
