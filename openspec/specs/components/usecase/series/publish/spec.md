# Publish

## Purpose

Publish lets the owning organizer operator take a complete DRAFT concert live: its DraftEvents enter the catalog as Events, claiming matching discovered Events; the Series becomes PUBLISHED; and when it is PUBLIC, followers of its performers are told about the new Events.

## Requirements

### Requirement: Only the owner

Publish SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another organizer's series
- **WHEN** an operator publishes a Series owned by another Organizer
- **THEN** Publish fails with PermissionDenied

### Requirement: Complete draft required

Publish SHALL fail with FailedPrecondition naming what is missing, leaving the Series DRAFT and announcing nothing, when the title is blank, when there is no performer, when there is no event, or when an event has no venue or no date. Description and cover image SHALL NOT be required.

#### Scenario: No performer
- **WHEN** the draft has no performer
- **THEN** Publish fails with FailedPrecondition and the Series stays DRAFT

#### Scenario: No cover image
- **WHEN** the draft has a title, a performer and a complete event but no description or cover image
- **THEN** Publish succeeds

### Requirement: Draft becomes live

Publish SHALL turn the draft into Events (Series.PublishDraft). A suppressed slot or a slot held by another Organizer SHALL fail the publish with FailedPrecondition and nothing is published; there is no override. A Series that is no longer DRAFT SHALL fail with FailedPrecondition.

#### Scenario: Claims a discovered event
- **WHEN** a DraftEvent's slot holds a discovered Event with fan TicketJourneys
- **THEN** that Event joins the Series with its id and TicketJourneys kept

#### Scenario: Suppressed slot
- **WHEN** a DraftEvent's slot was suppressed by an admin's delete
- **THEN** Publish fails with FailedPrecondition and the Series stays DRAFT

#### Scenario: Already published
- **WHEN** the owner publishes a PUBLISHED Series
- **THEN** Publish fails with FailedPrecondition

### Requirement: Unlisted series gets a share token

When the published Series is UNLISTED, Publish SHALL give it a new random share token (Series.SetUnlistedToken).

#### Scenario: Unlisted publish
- **WHEN** an UNLISTED draft is published
- **THEN** the Series is PUBLISHED with a share token and appears on no fan list

### Requirement: Public series announces new events per performer

When the published Series is PUBLIC and Series.PublishDraft added at least one Event, Publish SHALL announce the new concerts once per performing Artist of the Series, each announcement carrying all the added Event ids. Claimed Events SHALL NOT be announced. An UNLISTED Series SHALL announce nothing to followers. A failed announcement SHALL NOT fail Publish.

#### Scenario: Two performers
- **WHEN** a PUBLIC Series with two performers adds one Event
- **THEN** two announcements are made, one per performer, each carrying that Event id

#### Scenario: Only claimed events
- **WHEN** every DraftEvent claimed an existing discovered Event
- **THEN** no announcement is made to followers

### Requirement: Publish is always reported

After a successful publish, Publish SHALL report the publish for the Organizer with the Series and the number of added Events, whatever the visibility and even when no Event was added; a failed report SHALL NOT fail Publish. Publish SHALL return the Series with its Events and performers.

#### Scenario: Unlisted publish reported
- **WHEN** an UNLISTED Series is published
- **THEN** the publish is reported with the number of added Events
