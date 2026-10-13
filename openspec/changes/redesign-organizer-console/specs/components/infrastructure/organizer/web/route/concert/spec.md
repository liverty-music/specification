# Spec Delta

## Purpose

The organizer console page of one concert (one Series): its summary, performers and visibility, the publishing and cancelling of its dates together, and the list of its event dates, each leading to that event's page.

## ADDED Requirements

### Requirement: The concert's summary and its event dates

The page SHALL show the concert's title, type, visibility, cover image and performers, with 編集 (edit) opening the concert editor, and SHALL list its events in date order as items that are each one target, each with its date and start time in Japan time, its venue, its publish state as a labelled badge, and the state of its current or next TicketSale (none, scheduled, open or drawn). Selecting an event SHALL open that event's page. From 840 px the summary SHALL sit beside the list of events, and below it on narrower windows. A concert of another Organizer, or one that does not exist, SHALL show that the concert was not found with a link to Concerts.

#### Scenario: Tour with three dates

- **WHEN** an operator opens XX Tour 2026 with events on 3, 10 and 17 November
- **THEN** the three events are listed in that order with their venues and states, and selecting 3 November opens its event page

#### Scenario: Unknown concert

- **WHEN** an operator opens a concert address whose concert is not among the Organizer's concerts
- **THEN** the page says the concert was not found and links to Concerts

### Requirement: Publish or cancel the concert's dates together

While the concert has a draft date, the page SHALL offer 公開する (publish), which publishes the draft dates the operator chooses in one action (SeriesUseCase.Publish with those dates); the confirmation SHALL list the draft dates with each one chosen at first, and SHALL say that the performers' followers are notified once for the dates published together (a PUBLIC concert) or that no follower is notified (an UNLISTED concert), and that a published date cannot return to draft. While the concert has a published or draft date, the page SHALL offer 公演を中止 (cancel the concert) in its menu of further actions, which cancels every published and draft date in one action (SeriesUseCase.Cancel with no date named) after a confirmation saying that fans are told once, that draft dates are removed and that it cannot be undone. On success the page SHALL show the new states and confirm them in the snackbar. A concert whose dates are all cancelled SHALL offer neither.

#### Scenario: New tour published at once

- **WHEN** an operator presses 公開する on XX Tour 2026 with four draft dates, keeps all four chosen and confirms
- **THEN** one publish names the four dates, they are shown as 公開中, and the dialog had said followers are notified once

#### Scenario: Additional date on a published tour

- **WHEN** XX Tour 2026 has three published dates and one draft date added later, and the operator presses 公開する and confirms
- **THEN** only the draft date is published and the three published dates are unchanged

#### Scenario: One date left out

- **WHEN** the operator unchecks 24 November in the dialog and confirms
- **THEN** the other draft dates are published and 24 November stays draft

#### Scenario: Whole concert cancelled

- **WHEN** an operator presses 公演を中止 on a concert with published dates and confirms
- **THEN** one cancel is made with no date named and every date is shown as 中止

#### Scenario: Nothing to publish

- **WHEN** every date of a concert is published or cancelled
- **THEN** 公開する is not offered

