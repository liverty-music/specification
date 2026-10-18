# Spec Delta

## MODIFIED Requirements

### Requirement: Delete's outcome is shown

When Delete succeeds, the screen SHALL close the dialog, remove the Organizer from the list and return the detail to its no-selection state. When Delete fails with FailedPrecondition, the screen SHALL close the dialog, keep the Organizer listed and selected, and show `This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account.`, whatever reason the server gives. Any other failure SHALL be shown as an error with the Organizer kept.

#### Scenario: Delete succeeds

- **WHEN** Delete succeeds for the selected Organizer
- **THEN** it is no longer listed and the detail asks the admin to select an Organizer

#### Scenario: Delete blocked by an order

- **WHEN** Delete fails with FailedPrecondition because an Event of the Organizer has an Order that is not Refunded
- **THEN** the Organizer stays listed and selected, and the detail shows `This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account.` and not the server's message

#### Scenario: Delete fails otherwise

- **WHEN** Delete fails with Unavailable
- **THEN** the Organizer stays listed and selected, and the detail shows `Failed to delete the organizer.`

## ADDED Requirements

### Requirement: A refused Create says what to change

When Create fails, the screen SHALL keep the form's values and show, by error code: AlreadyExists, `That short name is already used by another organizer. Choose a different one.`; InvalidArgument, which after the screen's own checks of the name, short name and owner email means the sign-in service did not accept the owner email, `The sign-in service did not accept this owner email. Check it or use a different address.`; any other failure, `Failed to create the organizer.`

#### Scenario: Short name already used

- **WHEN** Create fails with AlreadyExists
- **THEN** the form shows `That short name is already used by another organizer. Choose a different one.`

#### Scenario: Owner email not accepted

- **WHEN** Create fails with InvalidArgument and the message `owner email was rejected by the identity provider (invalid_argument)`
- **THEN** the form shows `The sign-in service did not accept this owner email. Check it or use a different address.` and not the server's message

#### Scenario: Create fails otherwise

- **WHEN** Create fails with FailedPrecondition
- **THEN** the form shows `Failed to create the organizer.`
