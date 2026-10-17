## Purpose

The admin console's Organizers screen, where an admin creates Organizers, inspects one Organizer at a time and manages its lifecycle. This spec covers the Organizer list, each Organizer's status, the controls a deactivated Organizer keeps, Deactivate and Delete.

## ADDED Requirements

### Requirement: The list shows every Organizer with its status

The Organizers screen SHALL list every Organizer that OrganizerService.List returns, each with its name, short name and status label: `Provisioning`, `Active` or `Deactivated`.

#### Scenario: Organizers in every status

- **WHEN** the admin opens the Organizers screen while a provisioning, an active and a deactivated Organizer exist
- **THEN** all three are listed, labelled `Provisioning`, `Active` and `Deactivated`

### Requirement: The selected Organizer shows its status and the lifecycle action it allows

The selected Organizer's detail SHALL show its status label. It SHALL offer Deactivate only while the Organizer is provisioning or active, and Delete only while it is deactivated; it never offers both.

#### Scenario: Active Organizer

- **WHEN** the admin selects an active Organizer
- **THEN** the detail shows `Active` and offers Deactivate and not Delete

#### Scenario: Provisioning Organizer

- **WHEN** the admin selects a provisioning Organizer
- **THEN** the detail shows `Provisioning` and offers Deactivate and not Delete

#### Scenario: Deactivated Organizer

- **WHEN** the admin selects a deactivated Organizer
- **THEN** the detail shows `Deactivated` and offers Delete and not Deactivate

### Requirement: A deactivated Organizer's detail offers only what the Organizer still accepts

The detail of a deactivated Organizer SHALL NOT offer the controls whose calls a deactivated Organizer refuses: removing an Artist from its roster, searching for and associating an Artist, recording its business details and setting its platform fee rate. It SHALL still show its represented Artists without a Remove control. A provisioning or active Organizer's detail SHALL offer all of these controls.

#### Scenario: Deactivated Organizer hides refused controls

- **WHEN** the admin selects a deactivated Organizer
- **THEN** the detail offers no Remove control on the roster, no artist search or Associate control, no business-details form and no platform fee rate form

#### Scenario: Active Organizer keeps every control

- **WHEN** the admin selects an active Organizer
- **THEN** the detail offers Remove on each represented Artist, the artist search with Associate, the business-details form and the platform fee rate form

### Requirement: A successful Deactivate shows the Organizer deactivated

When Deactivate succeeds, the screen SHALL show the Organizer as `Deactivated` in the list and in the detail, offer Delete in place of Deactivate, hide the controls a deactivated Organizer refuses, and show its roster as empty, without the admin reloading the screen. When Deactivate fails, the screen SHALL show the error and leave the status and the action unchanged.

#### Scenario: Deactivate succeeds

- **WHEN** the admin deactivates an active Organizer that represents an Artist
- **THEN** the list and the detail show `Deactivated`, Delete replaces Deactivate, the artist search, the business-details form and the platform fee rate form are no longer offered, and the roster shows no Artists

#### Scenario: Deactivate fails

- **WHEN** Deactivate fails with Unavailable
- **THEN** the detail shows an error, the status label stays `Active` and Deactivate is still offered

### Requirement: Delete asks for confirmation first

Activating Delete SHALL open a modal confirmation dialog that names the Organizer by its name and short name and says that the Organizer and everything recorded for it are removed permanently. The Cancel control SHALL receive initial focus; Cancel and Escape SHALL close the dialog without deleting. OrganizerService.Delete SHALL be called only when the admin activates the dialog's Delete control, and that control SHALL be disabled while the call is in flight.

#### Scenario: Confirm deletes

- **WHEN** the admin activates Delete for a deactivated Organizer and then the dialog's Delete control
- **THEN** OrganizerService.Delete is called once for that Organizer

#### Scenario: Dismiss keeps the Organizer

- **WHEN** the admin activates Delete and then presses Escape or activates Cancel
- **THEN** the dialog closes, OrganizerService.Delete is not called and the Organizer stays listed

#### Scenario: Dialog names the Organizer

- **WHEN** the admin activates Delete for the Organizer `fan-test`
- **THEN** the dialog shows its name and the short name `fan-test`, and Cancel has focus

### Requirement: Delete's outcome is shown

When Delete succeeds, the screen SHALL close the dialog, remove the Organizer from the list and return the detail to its no-selection state. When Delete fails with FailedPrecondition, the screen SHALL close the dialog, keep the Organizer listed and selected, and show that it cannot be deleted together with the reason the server gives: an Order that is not Refunded, a Settlement that is not Reversed, a payout account, or the Organizer not being deactivated. Any other failure SHALL be shown as an error with the Organizer kept.

#### Scenario: Delete succeeds

- **WHEN** Delete succeeds for the selected Organizer
- **THEN** it is no longer listed and the detail asks the admin to select an Organizer

#### Scenario: Delete blocked by an order

- **WHEN** Delete fails with FailedPrecondition because an Event of the Organizer has an Order that is not Refunded
- **THEN** the Organizer stays listed and selected, and the detail says it cannot be deleted because of an Order that is not refunded

#### Scenario: Delete fails otherwise

- **WHEN** Delete fails with Unavailable
- **THEN** the Organizer stays listed and selected, and the detail shows an error
