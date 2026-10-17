# Organizer Series RPC

## Purpose

The organizer-facing Series service boundary: how a member's sign-in is turned into their own Organizer before any authoring call runs, and which drafts the boundary rejects before the usecase sees them.

## Requirements

### Requirement: Every authoring call acts for the caller's own active Organizer

Every call of the organizer Series service — Create, Update, Publish, Cancel, List, RegenerateShareUrl and SetCoverImage — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. A failure of ResolveCaller SHALL be returned unchanged and nothing is stored: PermissionDenied when no Organizer is linked to the Organization or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated. Ownership of the Series named in a request is checked by the usecase, not here.

#### Scenario: Member of an active Organizer lists concerts

- **WHEN** a member of an active Organizer calls List
- **THEN** the Organizer's own Series are returned with their Concerts

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** every authoring call fails with PermissionDenied and nothing is stored

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every authoring call fails with FailedPrecondition

### Requirement: A draft names at least one performer and one event

Create and Update SHALL fail with InvalidArgument, before any usecase runs, when the draft names no Artist or no event.

#### Scenario: Draft without events

- **WHEN** a member calls Create with a draft that has a performer and no event
- **THEN** it fails with InvalidArgument and no Series is created

### Requirement: RegenerateShareUrl returns the new token

RegenerateShareUrl SHALL return the Series' new unlisted share token; the organizer console builds the share link from it.

#### Scenario: New token

- **WHEN** a member regenerates the share link of their UNLISTED Series
- **THEN** the response carries the new token and the old share link stops working

### Requirement: What a returned series carries

Create, Update, Publish and List SHALL return each Series they act on or list together with its dates as Concerts and, once each, every Artist those Concerts refer to; a Concert carries only the id of its Series (through its Event) and the ids of its Artists. Every Event of the Series is returned whatever its publish state, each as a Concert carrying that Event's publish state and its own performers. Every returned Series SHALL carry its description, cover image, visibility and publish state when it has them. The share token SHALL be returned only by RegenerateShareUrl.

#### Scenario: Tour with one performer

- **WHEN** a member lists their Organizer's Series and one of them has three dates performed by the same Artist
- **THEN** the response carries that Series once with three Concerts, and that Artist once

#### Scenario: Draft series

- **WHEN** a member creates a draft Series with two dates and one performer
- **THEN** the response carries the DRAFT Series with two Concerts, each referring to that performer
