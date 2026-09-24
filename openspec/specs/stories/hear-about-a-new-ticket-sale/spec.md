# Hear about a new ticket sale

## Purpose

A fan who tracks an event of a tour is told, once, when a new ticket sales phase for that tour is published, while fans who only follow the artist are not.

## Requirements

### Requirement: A new sales phase reaches the fans tracking its series

When SalesPhaseDiscoveryUseCase.DiscoverForArtist finds a sales phase for a series that was not known before, SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase SHALL announce it, and every fan whose ticket journey on an event of that series is Tracking SHALL receive one push notification about it on each registered browser, titled in their language (チケット販売情報の新着 in Japanese, New Ticket Sales Phase otherwise), and SHALL have one sales-phase announcement Notification recorded for them.

#### Scenario: Tracking fan hears about the new phase

- **WHEN** a fan tracks one event of a tour, and the daily discovery finds a new presale for that tour
- **THEN** the fan's browser receives one New Ticket Sales Phase push and the fan has one sales-phase announcement Notification

#### Scenario: Follower who tracks nothing

- **WHEN** a fan follows the artist but tracks no event of the tour
- **THEN** the fan receives no push and has no Notification about the phase

#### Scenario: Fan who has already applied

- **WHEN** a fan's only journey on the tour is Applied
- **THEN** the fan receives no push about the new phase

### Requirement: A phase is announced once

A sales phase discovered again on a later day SHALL NOT be announced again. A repeat of the same announcement after a failure SHALL replace the earlier push on the fan's browser, not add a second one.

#### Scenario: Same phase found the next day

- **WHEN** the daily discovery finds the same presale again the next day
- **THEN** no fan receives another push about it

### Requirement: Fans without a browser still get the record

A tracking fan with no registered browser SHALL receive no push, and their sales-phase announcement Notification SHALL be recorded as Failed because they have no registered browser.

#### Scenario: No registered browser

- **WHEN** a tracking fan has never allowed push notifications and a new phase is found
- **THEN** nothing is pushed to the fan and their Notification is Failed with the reason no active push subscription
