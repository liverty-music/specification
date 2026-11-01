# components/infrastructure/organizer/web/route/concert Specification

## Purpose
The organizer console page of one concert (one Series): its summary, performers and visibility, its seat types (席種) with their prices, the publishing and cancelling of its dates together, and the list of its event dates, each leading to that event's page.

## Requirements

### Requirement: The concert's summary and its event dates

The page SHALL show the concert's title, type, visibility, cover image and performers, with 編集 (edit) opening the concert editor, and SHALL list its events in date order as items that are each one target, each with its date and start time in Japan time, its venue, its publish state as a labelled badge, and the state of its current or next TicketSale (none, scheduled, open or drawn). Selecting an event SHALL open that event's page. From 840 px the summary SHALL sit beside the list of events, and below it on narrower windows. A concert of another Organizer, or one that does not exist, SHALL show that the concert was not found with a link to Concerts.

#### Scenario: Tour with three dates

- **WHEN** a member opens XX Tour 2026 with events on 3, 10 and 17 November
- **THEN** the three events are listed in that order with their venues and states, and selecting 3 November opens its event page

#### Scenario: Unknown concert

- **WHEN** a member opens a concert address whose concert is not among the Organizer's concerts
- **THEN** the page says the concert was not found and links to Concerts

### Requirement: Publish or cancel the concert's dates together

While the concert has a draft date, the page SHALL offer 公開する (publish), which publishes the draft dates the member chooses in one action (SeriesUseCase.Publish with those dates); the confirmation SHALL list the draft dates with each one chosen at first, and SHALL say that the performers' followers are notified once for the dates published together (a PUBLIC concert) or that no follower is notified (an UNLISTED concert), and that a published date cannot return to draft. While the concert has a published or draft date, the page SHALL offer 公演を中止 (cancel the concert) in its menu of further actions, which cancels every published and draft date in one action (SeriesUseCase.Cancel with no date named) after a confirmation saying that fans are told once, that draft dates are removed and that it cannot be undone. On success the page SHALL show the new states and confirm them in the snackbar. When the publish is refused with FailedPrecondition, the snackbar SHALL say that a chosen date's venue, date and start time are already used by another concert or by a cancelled date and that the member changes that date's date or start time in the concert editor, SHALL offer no retry, and the page SHALL show the dates' current states. A concert whose dates are all cancelled SHALL offer neither.

#### Scenario: New tour published at once

- **WHEN** a member presses 公開する on XX Tour 2026 with four draft dates, keeps all four chosen and confirms
- **THEN** one publish names the four dates, they are shown as 公開中, and the dialog had said followers are notified once

#### Scenario: Additional date on a published tour

- **WHEN** XX Tour 2026 has three published dates and one draft date added later, and the member presses 公開する and confirms
- **THEN** only the draft date is published and the three published dates are unchanged

#### Scenario: One date left out

- **WHEN** the member unchecks 24 November in the dialog and confirms
- **THEN** the other draft dates are published and 24 November stays draft

#### Scenario: Date already used by another concert

- **WHEN** the member publishes XX Tour 2026's draft date of 11 December 18:00 at Zepp Haneda, and the Organizer's concert YY Live already has a date there
- **THEN** the snackbar says the venue, date and start time are already used and to change the date or start time in the concert editor, no retry is offered, and the draft date stays 下書き

#### Scenario: Whole concert cancelled

- **WHEN** a member presses 公演を中止 on a concert with published dates and confirms
- **THEN** one cancel is made with no date named and every date is shown as 中止

#### Scenario: Nothing to publish

- **WHEN** every date of a concert is published or cancelled
- **THEN** 公開する is not offered

### Requirement: The concert's seat types

The page SHALL show a section 席種 (seat types) listing the concert's SeatTypes, read with SeatTypeService.ListBySeries, each with its name and price 税込 (tax-inclusive), and SHALL say that every date of the concert sells from these seat types and that the quantity of each is set on each date's Sales tab. It SHALL offer 席種を追加 (add a seat type), which asks for a name of 1 to 50 characters and a price of 1 to 1,000,000 yen and creates the SeatType with SeatTypeService.Create after a confirmation saying that the name and price cannot be changed afterwards. A SeatType that no date stocks SHALL offer 削除 (delete), which deletes it with SeatTypeService.Delete after confirmation; one that a date stocks SHALL offer no delete. A name already used by another seat type of the concert SHALL be shown as an error next to the name, and nothing is saved. A concert whose dates are all cancelled SHALL offer neither action.

#### Scenario: Dome tour seat types

- **WHEN** a member adds S席 at 12,000 yen, A席 at 9,000 yen and B席 at 7,000 yen to XX Dome Tour 2026
- **THEN** the section lists the three seat types with 12,000円, 9,000円 and 7,000円, and says the quantities are set on each date

#### Scenario: Price mistake before stocking

- **WHEN** a member added S席 at 1,200 yen by mistake and no date stocks it
- **THEN** S席 offers 削除, and after deleting it the member adds S席 at 12,000 yen

#### Scenario: Seat type in use

- **WHEN** the 3 November date stocks S席
- **THEN** S席 offers no delete and no way to change its name or price

#### Scenario: Name already used

- **WHEN** the concert has S席 and the member adds another seat type named S席
- **THEN** an error is shown next to the name and nothing is saved
