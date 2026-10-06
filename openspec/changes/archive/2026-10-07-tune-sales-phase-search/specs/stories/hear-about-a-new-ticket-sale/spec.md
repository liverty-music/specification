# Spec Delta

## MODIFIED Requirements

### Requirement: A new sales phase reaches the fans tracking its series

When SalesPhaseDiscoveryUseCase.DiscoverForArtist finds, for a series that a fan tracks, a sales phase that has not opened and was not known before, SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase SHALL announce it. Every fan whose ticket journey on an event of that series is Tracking SHALL then:

- receive one push notification about it on each registered browser, naming the opening date, the method and the tour, in their language
- have one sales-phase announcement Notification recorded for them

Tapping the push SHALL open the detail sheet of the fan's earliest upcoming tracked event of the series.

#### Scenario: Tracking fan hears about the new phase

- **WHEN** a fan tracks the 20 December event of 星降る晩餐会, and the daily discovery finds a first-come presale opening on 6 October 19:00
- **THEN** the fan's browser receives one push titled チケット先着販売のお知らせ whose text is 10/6(火) 19:00からチケットの先着販売スタート!! followed by a line break and 星降る晩餐会
- **AND** the fan has one sales-phase announcement Notification

#### Scenario: Tapping the push

- **WHEN** the fan taps that push
- **THEN** the app opens the detail sheet of the fan's tracked 20 December event

#### Scenario: Follower who tracks nothing

- **WHEN** a fan follows the artist but tracks no event of the tour
- **THEN** the tour is not searched, and the fan receives no push and has no Notification about its sales

#### Scenario: Fan who has already applied

- **WHEN** a fan's only journey on the tour is Applied
- **THEN** the fan receives no push about the new phase
