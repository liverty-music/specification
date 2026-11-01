# Spec Delta

## MODIFIED Requirements

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
