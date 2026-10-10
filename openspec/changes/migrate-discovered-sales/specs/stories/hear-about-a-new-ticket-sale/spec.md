# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: A new sales phase reaches the fans tracking its series`
- TO: `### Requirement: A new discovered sale reaches the fans tracking its series`
- FROM: `### Requirement: A phase is announced once`
- TO: `### Requirement: A discovered sale is announced once`

## MODIFIED Requirements

### Requirement: A new discovered sale reaches the fans tracking its series

When TicketSaleDiscoveryUseCase.DiscoverForArtist finds, for a series that a fan tracks, a ticket sale that has not opened and was not known before, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale SHALL announce it. Every fan whose ticket journey on an event of that series is Tracking SHALL then:

- receive one push notification about it on each registered browser, naming the opening date, the method and the tour, in their language
- have one ticket sale announcement Notification recorded for them

Tapping the push SHALL open the detail sheet of the fan's earliest upcoming tracked event of the series.

#### Scenario: Tracking fan hears about the new phase
- **WHEN** a fan tracks the 20 December event of 星降る晩餐会, and the daily discovery finds a first-come presale opening on 6 October 19:00
- **THEN** the fan's browser receives one push titled チケット先着販売のお知らせ whose text is 10/6(火) 19:00からチケットの先着販売スタート!! followed by a line break and 星降る晩餐会
- **AND** the fan has one ticket sale announcement Notification

#### Scenario: Tapping the push
- **WHEN** the fan taps that push
- **THEN** the app opens the detail sheet of the fan's tracked 20 December event

#### Scenario: Follower who tracks nothing
- **WHEN** a fan follows the artist but tracks no event of the tour
- **THEN** the tour is not searched, and the fan receives no push and has no Notification about its sales

#### Scenario: Fan who has already applied
- **WHEN** a fan's only journey on the tour is Applied
- **THEN** the fan receives no push about the new sale

### Requirement: A discovered sale is announced once

A discovered sale found again on a later day SHALL NOT be announced again. A repeat of the same announcement after a failure SHALL replace the earlier push on the fan's browser, not add a second one.

#### Scenario: Same phase found the next day
- **WHEN** the daily discovery finds the same presale again the next day
- **THEN** no fan receives another push about it

### Requirement: Fans without a browser still get the record

A tracking fan with no registered browser SHALL receive no push, and their ticket sale announcement Notification SHALL be recorded as Failed because they have no registered browser.

#### Scenario: No registered browser
- **WHEN** a tracking fan has never allowed push notifications and a new discovered sale is found
- **THEN** nothing is pushed to the fan and their Notification is Failed with the reason no active push subscription
