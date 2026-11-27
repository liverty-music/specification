## MODIFIED Requirements

### Requirement: The concert's summary and its event dates

The page SHALL show the concert's title, type, visibility, cover image and performers, with 編集 (edit) opening the concert editor, and SHALL list its events in date order as items that are each one target, each with its date and start time at its Venue's local time, labelled with the name of the Venue's time zone and, when that zone is not Asia/Tokyo, the Japan time in parentheses (global/i18n "Dates and times in the zone they belong to"), its venue, its publish state as a labelled badge, and the state of its current or next TicketSale (none, scheduled, open or drawn). Selecting an event SHALL open that event's page. From 840 px the summary SHALL sit beside the list of events, and below it on narrower windows. A concert of another Organizer, or one that does not exist, SHALL show that the concert was not found with a link to Concerts.

#### Scenario: Tour with three dates

- **WHEN** a member opens XX Tour 2026 with events on 3, 10 and 17 November
- **THEN** the three events are listed in that order with their venues and states, and selecting 3 November opens its event page

#### Scenario: Date in Japan

- **WHEN** a member opens a concert with an event on 2026-11-03 at 18:00 at a Venue in Tokyo
- **THEN** the event is listed as 11月3日(火) 18:00 日本時間

#### Scenario: Date abroad

- **WHEN** a member opens a concert with an event on 2027-02-20 at 19:30 at a Venue in London
- **THEN** the event is listed as 2月20日(土) 19:30 ロンドン時間（日本時間 2月21日(日) 04:30）

#### Scenario: Unknown concert

- **WHEN** a member opens a concert address whose concert is not among the Organizer's concerts
- **THEN** the page says the concert was not found and links to Concerts
