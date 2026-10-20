# stories/retire-an-organizer Specification

## Purpose
An admin retires an Organizer that should no longer exist, such as a test Organizer: it is deactivated so the identities of its Organization can no longer sign in, then deleted permanently from the admin console's Organizers screen.

```mermaid
usecase-beta
direction LR
actor Admin("admin")
systemBoundary "Liverty Music"
  Goal("Retire an organizer")
  OrganizerUseCaseList("OrganizerUseCase.List")
  OrganizerUseCaseDeactivate("OrganizerUseCase.Deactivate")
  OrganizerUseCaseDelete("OrganizerUseCase.Delete")
end
Admin --> Goal
Goal ..> : include OrganizerUseCaseList
Goal ..> : include OrganizerUseCaseDeactivate
Goal ..> : include OrganizerUseCaseDelete
```

## Requirements

### Requirement: An admin deactivates and then deletes an Organizer from the Organizers screen

An admin SHALL be able to retire an Organizer entirely from the Organizers screen: Deactivate turns it off and the screen shows it deactivated; Delete then removes it, with its files, its Organization at the identity provider and every record kept for it, unless a purchase or a payout account blocks the deletion.

#### Scenario: Deactivated Organizer is shown deactivated

- **WHEN** the admin opens the Organizers screen after an Organizer was deactivated
- **THEN** the Organizer is labelled `Deactivated`, and its detail offers Delete and not Deactivate

#### Scenario: Deleted Organizer is gone

- **WHEN** the admin deletes a deactivated Organizer with no Orders and no payout account and confirms
- **THEN** the Organizer is no longer listed, also after the screen is reloaded, and OrganizerService.Get for its id fails with NotFound
