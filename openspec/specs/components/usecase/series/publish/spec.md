# Publish

## Purpose

Publish lets a member of the owning Organizer take DRAFT Events of a concert live, all of them or only the named ones, including dates added after an earlier publish: they become PUBLISHED, claiming matching discovered Events, and when the Series is PUBLIC, followers of its performers are told about the newly published Events only.

## Requirements

### Requirement: Only the owner

Publish SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another Organizer's series
- **WHEN** a member publishes a Series owned by another Organizer
- **THEN** Publish fails with PermissionDenied

### Requirement: Complete draft required

Publish SHALL fail with FailedPrecondition naming what is missing, publishing nothing and announcing nothing, when the title is blank, when there is no performer, when there is no Event to publish, or when an Event to publish has no venue or no date. Description and cover image SHALL NOT be required.

#### Scenario: No performer
- **WHEN** the draft has no performer
- **THEN** Publish fails with FailedPrecondition and every Event stays DRAFT

#### Scenario: No cover image
- **WHEN** the draft has a title, a performer and a complete event but no description or cover image
- **THEN** Publish succeeds

### Requirement: Draft becomes live

Publish SHALL take a Series and, optionally, some of its Events; when no Event is named it SHALL publish every DRAFT Event of the Series. It SHALL publish them with Series.PublishEvents. A suppressed slot, a slot held by another Organizer or a slot held by a CANCELLED Event SHALL fail the publish with FailedPrecondition and nothing is published; there is no override. A named Event that is not DRAFT, or a Series with no DRAFT Event when none is named, SHALL fail with FailedPrecondition.

#### Scenario: Claims a discovered event
- **WHEN** a DRAFT Event's slot holds a discovered Event with fan TicketJourneys
- **THEN** that Event joins the Series as PUBLISHED with its id and TicketJourneys kept

#### Scenario: Suppressed slot
- **WHEN** a DRAFT Event's slot was suppressed by an admin's delete
- **THEN** Publish fails with FailedPrecondition and every Event stays DRAFT

#### Scenario: Already published
- **WHEN** the owner publishes a Series that has no DRAFT Event
- **THEN** Publish fails with FailedPrecondition

#### Scenario: Additional date on a published tour
- **WHEN** the owner publishes the one DRAFT Event of a Series whose other Events are PUBLISHED
- **THEN** that Event becomes PUBLISHED and the other Events are unchanged

#### Scenario: Only the named date
- **WHEN** a Series has two DRAFT Events and the owner names one of them
- **THEN** only the named Event is published and the other stays DRAFT

### Requirement: Unlisted series gets a share token

When the Series is UNLISTED and has no share token yet, Publish SHALL give it a new random share token (Series.SetUnlistedToken). A Series that already has a share token SHALL keep it.

#### Scenario: Unlisted publish
- **WHEN** an UNLISTED draft is published
- **THEN** the Series has a PUBLISHED Event and a share token and appears on no fan list

#### Scenario: New date keeps the share link
- **WHEN** a new date of an UNLISTED Series that already has a share token is published
- **THEN** the share token is unchanged

### Requirement: Public series announces new events per performer

When the Series is PUBLIC and Series.PublishEvents added at least one Event, Publish SHALL announce the new concerts once per performing Artist of the Series, each announcement carrying all the Event ids added by this publish. Claimed Events, and Events published before, SHALL NOT be announced. An UNLISTED Series SHALL announce nothing to followers. A failed announcement SHALL NOT fail Publish.

#### Scenario: Two performers
- **WHEN** a PUBLIC Series with two performers adds one Event
- **THEN** two announcements are made, one per performer, each carrying that Event id

#### Scenario: Only claimed events
- **WHEN** every published DRAFT Event claimed an existing discovered Event
- **THEN** no announcement is made to followers

#### Scenario: Additional date announced alone
- **WHEN** a PUBLIC Series with three PUBLISHED Events publishes one new date
- **THEN** the announcement carries only the new Event's id

### Requirement: Publish is always reported

After a successful publish, Publish SHALL report the publish for the Organizer with the Series and the number of added Events, whatever the visibility and even when no Event was added; a failed report SHALL NOT fail Publish. Publish SHALL return the Series with its Events and performers.

#### Scenario: Unlisted publish reported
- **WHEN** an UNLISTED Series is published
- **THEN** the publish is reported with the number of added Events
