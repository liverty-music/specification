# components/infrastructure/admin/web/route/organizers Specification

## Purpose
The admin console's Organizers screen, where an admin creates Organizers, inspects one Organizer at a time and manages its lifecycle. This spec covers the Organizer list, each Organizer's status, the controls a deactivated Organizer keeps, Deactivate and Delete.

## Requirements

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

When Delete succeeds, the screen SHALL close the dialog, remove the Organizer from the list and return the detail to its no-selection state. When Delete fails with FailedPrecondition, the screen SHALL close the dialog, keep the Organizer listed and selected, and show `This organizer cannot be deleted while it has a paid order, a settlement that is not reversed, a purchase in progress, or a payout account.`, whatever reason the server gives. Any other failure SHALL be shown as an error with the Organizer kept.

#### Scenario: Delete succeeds

- **WHEN** Delete succeeds for the selected Organizer
- **THEN** it is no longer listed and the detail asks the admin to select an Organizer

#### Scenario: Delete blocked by an order

- **WHEN** Delete fails with FailedPrecondition because an Event of the Organizer has a Paid Order
- **THEN** the Organizer stays listed and selected, and the detail shows `This organizer cannot be deleted while it has a paid order, a settlement that is not reversed, a purchase in progress, or a payout account.` and not the server's message

#### Scenario: Delete fails otherwise

- **WHEN** Delete fails with Unavailable
- **THEN** the Organizer stays listed and selected, and the detail shows `Failed to delete the organizer.`

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

### Requirement: An admin creates a test Artist for the Organizer

A provisioning or active Organizer's detail SHALL offer `Create test artist` beside the artist search, with a name field. A test Artist has a name the admin chooses and a music-catalog id the screen generates at random, so it matches no real artist. Under the field the screen SHALL show `Use a name no real artist uses.` On submit, the screen SHALL register the Artist with ArtistService.Create, then associate it with the Organizer with OrganizerService.AssociateArtist, and show it in the roster. When the association fails after the Artist was registered, the screen SHALL keep that Artist and offer to retry only the association, so a retry registers no second Artist. An empty name SHALL be refused by the screen without a call. A deactivated Organizer's detail SHALL NOT offer `Create test artist`.

#### Scenario: Test artist created and associated

- **WHEN** the admin enters `E2E Test Artist` for an active Organizer and submits
- **THEN** ArtistService.Create is called once with that name and a generated music-catalog id, the Artist is associated with the Organizer, and the roster lists `E2E Test Artist`

#### Scenario: Association fails after registration

- **WHEN** ArtistService.Create succeeds and OrganizerService.AssociateArtist fails with Unavailable
- **THEN** the screen shows an error and offers to retry the association, and retrying calls only OrganizerService.AssociateArtist for the same Artist

#### Scenario: Empty name

- **WHEN** the admin submits `Create test artist` with an empty name
- **THEN** no call is made and the field asks for a name

### Requirement: A represented Artist opens its concerts

Each Artist in the selected Organizer's roster SHALL link to the Artist concerts screen for that Artist, whatever the Organizer's status. The link SHALL carry the Artist's id only; the screen reads everything it shows from the server.

#### Scenario: Open an artist's concerts

- **WHEN** the admin activates the link of a represented Artist
- **THEN** the Artist concerts screen opens for that Artist
