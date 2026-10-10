## MODIFIED Requirements

### Requirement: Every authoring call acts for the caller's own active Organizer

Every call of the organizer Series service — Create, Update, Publish, Cancel, List, RegenerateToken, CreateMediaUploadURL and AttachMedia — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing is stored: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated. Ownership of the Series named in a request is checked by the usecase, not here.

#### Scenario: Operator of an active Organizer lists concerts

- **WHEN** an operator of an active Organizer calls List
- **THEN** the Organizer's own Series are returned with their Concerts

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** every authoring call fails with PermissionDenied and nothing is stored

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every authoring call fails with FailedPrecondition

## ADDED Requirements

### Requirement: What a returned series carries

Create, Update, Publish and List SHALL return each Series they act on or list together with its dates as Concerts and, once each, every Artist those Concerts refer to; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. A DRAFT Series' dates are its DraftEvents, each returned as a Concert with the Series' draft performers. Every returned Series SHALL carry its description, cover image, visibility and publish state when it has them. The share token SHALL be returned only by RegenerateToken.

#### Scenario: Tour with one performer

- **WHEN** an operator lists their Organizer's Series and one of them has three dates performed by the same Artist
- **THEN** the response carries that Series once with three Concerts, and that Artist once

#### Scenario: Draft series

- **WHEN** an operator creates a draft Series with two dates and one performer
- **THEN** the response carries the DRAFT Series with two Concerts, each referring to that performer
