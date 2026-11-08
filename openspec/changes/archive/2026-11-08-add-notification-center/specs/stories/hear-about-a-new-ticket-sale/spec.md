## MODIFIED Requirements

### Requirement: A new discovered sale reaches the fans tracking its series

When TicketSaleDiscoveryUseCase.DiscoverForArtist finds, for a series that a fan tracks, a ticket sale that has not opened and was not known before, TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale SHALL announce it. Every fan whose ticket journey on an event of that series is Tracking SHALL then:

- receive one push notification about it on each registered browser, naming the artist, the opening date, the method and the tour, in their language
- have one ticket sale announcement Notification recorded for them

Tapping the push SHALL open the detail sheet of the fan's earliest upcoming tracked event of the series.

#### Scenario: Tracking fan hears about the new phase
- **WHEN** a fan tracks the 20 December event of 星降る晩餐会 by Vaundy, and the daily discovery finds a first-come presale opening on 6 October 19:00
- **THEN** the fan's browser receives one push titled [Vaundy] 先着販売のお知らせ whose text is 10/6(火) 19:00から先着販売スタート!! followed by a line break and 星降る晩餐会
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

## ADDED Requirements

### Requirement: Fans without a browser find the announcement in the notification center

A tracking fan with no registered browser SHALL receive no push, and their ticket sale announcement Notification SHALL still be recorded, so the notification center lists it.

#### Scenario: Never allowed push notifications
- **WHEN** a tracking fan has never allowed push notifications and a new discovered sale is found
- **THEN** nothing is pushed to the fan and the notification center lists the announcement

## REMOVED Requirements

### Requirement: Fans without a browser still get the record
**Reason**: A Notification no longer records a delivery outcome; replaced by "Fans without a browser find the announcement in the notification center".
**Migration**: None.
