## MODIFIED Requirements

### Requirement: Each call runs one OrganizerUseCase method and returns the short name

Each call SHALL run one usecase method:
- Create SHALL run OrganizerUseCase.Create with the name, the short name and the owner email and return the created Organizer.
- Get and List SHALL run OrganizerUseCase.Get and OrganizerUseCase.List for any Organizer the admin names.
- AssociateArtist, DisassociateArtist, Deactivate, Delete, SetBusinessDetails and SetPlatformFeeRate SHALL run the usecase method of the same name.

The admin Organizer service SHALL NOT list an Organizer's Artists; the admin artist service does (ListByOrganizer). Errors from the usecase SHALL be returned unchanged. An Organizer is returned with its id, name, short name, status, legal name, representative name, business address, business phone number, contact email and platform fee rate. The status is one of provisioning, active and deactivated, as the Organizer entity defines it.

#### Scenario: Admin lists Organizers and inspects a roster

- **WHEN** an admin lists Organizers and then requests one Organizer's Artists
- **THEN** it returns every Organizer with its short name, and the Artists that Organizer represents come from the admin artist service's ListByOrganizer, not from the Organizer service

#### Scenario: Admin lists Organizers in every status

- **WHEN** an admin lists Organizers while a provisioning, an active and a deactivated Organizer exist
- **THEN** each is returned with its own status: provisioning, active and deactivated

#### Scenario: Admin reads any Organizer

- **WHEN** an admin calls Get for a deactivated Organizer
- **THEN** it returns that Organizer's id, name, short name, status deactivated, business details and platform fee rate

#### Scenario: Admin deletes a deactivated Organizer

- **WHEN** an admin calls Delete for a deactivated Organizer
- **THEN** OrganizerUseCase.Delete runs and the call succeeds with an empty response

#### Scenario: Delete refused

- **WHEN** OrganizerUseCase.Delete fails with FailedPrecondition
- **THEN** Delete fails with FailedPrecondition

#### Scenario: Admin records business details

- **WHEN** an admin calls SetBusinessDetails with all five business details
- **THEN** OrganizerUseCase.SetBusinessDetails runs and the Organizer is returned with them

#### Scenario: Short name already used

- **WHEN** OrganizerUseCase.Create fails with AlreadyExists for the short name
- **THEN** Create fails with AlreadyExists
