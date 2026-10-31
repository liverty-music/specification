# Spec Delta

## MODIFIED Requirements

### Requirement: The event header and its actions

The page SHALL show the event's date and start time in Japan time, its venue and its publish state as a labelled badge, and SHALL offer the actions that apply to the event's state: 公開する (publish) for a draft event, which publishes this date only, as the page's main action, and, in a menu of further actions, 中止する (cancel) for an event that is not cancelled and 公演を編集 (edit the concert), which opens the concert editor. Publishing and cancelling SHALL ask for confirmation first, naming the effect (for a draft date, that 中止する removes it); the publish confirmation SHALL say that publishing this date alone notifies followers for this date, and point to the concert page to publish several dates with one notification, and on success the page SHALL show the new state and confirm it in the snackbar. When the publish is refused with FailedPrecondition, the snackbar SHALL say that the date's venue, date and start time are already used by another concert or by a cancelled date and that the member changes the date or start time in the concert editor, SHALL offer no retry, and the page SHALL show the event's current state. A cancelled event SHALL show that it is cancelled and offer no action. The page SHALL have two tabs, 販売 (Sales) and 受付 (Reception), each with its own address so a tab can be reopened or shared; the page opens on 販売. An event of another Organizer, or one that does not exist, SHALL show that the event was not found with a link to its concert or to Concerts.

#### Scenario: Draft event

- **WHEN** a member opens a draft event of XX Tour 2026 on 3 November at Zepp Haneda
- **THEN** the header shows 11月3日(火) 18:00 JST · Zepp Haneda with the badge 下書き and offers 公開する, with 中止する and 公演を編集 in its menu

#### Scenario: Publish confirmed

- **WHEN** the member presses 公開する and confirms in the dialog
- **THEN** the badge becomes 公開中 and the snackbar says the event was published

#### Scenario: Publish refused for a used slot

- **WHEN** the member publishes a draft event on 11 December 18:00 at Zepp Haneda, and another concert of the Organizer already has a date there
- **THEN** the snackbar says the venue, date and start time are already used and to change the date or start time in the concert editor, no retry is offered, and the badge stays 下書き

#### Scenario: Reception tab address

- **WHEN** a member opens the Reception tab's address directly after signing in
- **THEN** the event page opens with 受付 selected
