## Purpose

How every backend process announces a fact to the rest of the system and receives one: an announcement is recorded with the change it announces, delivered at least once under one id, handled once by each receiver, and never carries the personal data that must be protected. Work for one receiver is started as a workflow, not announced.

## ADDED Requirements

### Requirement: An announcement is recorded with its fact

An entity operation that announces SHALL record the announcement together with the change it announces: both are stored or neither is. An operation that finds its change already made SHALL change nothing and announce nothing. No announcement SHALL be made without a stored change.

#### Scenario: Change and announcement together

- **WHEN** an operation stores a change and records its announcement
- **THEN** the change is stored and its announcement is delivered

#### Scenario: Announcement cannot be recorded

- **WHEN** the announcement of a change cannot be recorded
- **THEN** the operation fails and the change is not stored

#### Scenario: Change already made

- **WHEN** a retried call, a redelivered announcement or a workflow step that runs again calls an operation whose change is already stored
- **THEN** nothing is changed and nothing is announced

### Requirement: An announcement is delivered at least once under one id

Every recorded announcement SHALL be delivered to its receivers, also when a backend process stops between recording and delivery. The id an announcement gets when it is recorded SHALL be the id of every delivery of it. Receivers SHALL treat deliveries with the same id as one announcement.

#### Scenario: Process stops before delivery

- **WHEN** a process stops after a change and its announcement were recorded and before the announcement was delivered
- **THEN** the announcement is delivered after the process starts again

#### Scenario: Delivered twice

- **WHEN** an announcement is delivered, and delivered again with the same id because the delivery was not confirmed
- **THEN** each receiver acts on it once and product analytics records it once

### Requirement: An announcement that cannot be delivered is reported

An announcement still not delivered 10 minutes after it was recorded SHALL be reported for an admin, with the subject and the time it was recorded.

#### Scenario: Broker unreachable

- **WHEN** announcements cannot be delivered for 10 minutes
- **THEN** an admin is alerted, and the announcements are delivered once delivery works again

### Requirement: An announcement never carries the ticket-face identity details or push credentials

An announcement SHALL NOT carry a User's full name, phone number or the display name given by the identity provider, nor a PushSubscription's push address or keys. It MAY carry an email address.

#### Scenario: New push subscription announced

- **WHEN** a PushSubscription is announced
- **THEN** the announcement carries its id, its User and its device family, and neither its push address nor its keys

#### Scenario: New user announced

- **WHEN** a User with a full name, a phone number and a display name from the identity provider is announced
- **THEN** the announcement carries the User's id and email address, and none of the full name, the phone number and the display name

### Requirement: Work for one receiver is started as a workflow

A request for one receiver to do work, with no stored change behind it, SHALL start that receiver's workflow instead of being announced. The workflow SHALL be named after the business key of the request, so a repeated request with the same key starts nothing new. Work that follows a stored change runs from that change's announcement. A request whose receiver runs only in a dedicated process (series image processing) SHALL instead be recorded together with the stored change it follows and delivered like an announcement.

#### Scenario: Same request twice

- **WHEN** the same request, with the same business key, is made twice
- **THEN** the receiver's workflow runs once

#### Scenario: Request for a dedicated process

- **WHEN** a SeriesImage is attached to a Series
- **THEN** the request to process it, naming the Series, is recorded with the SeriesImage and delivered at least once to series image processing
