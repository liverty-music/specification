# Spec Delta

## Purpose

The organizer console page of one concert (one Series): its summary, performers, visibility and share link, and the list of its event dates, each leading to that event's page.

## ADDED Requirements

### Requirement: The concert's summary and its event dates

The page SHALL show the concert's title, type, visibility, cover image and performers, with 編集 (edit) opening the concert editor, and SHALL list its events in date order, each with its date and start time in Japan time, its venue, its publish state as a labelled badge, and the state of its current or next TicketSale (none, scheduled, open or drawn). Each event SHALL open that event's page. A concert of another Organizer, or one that does not exist, SHALL show that the concert was not found with a link to Concerts.

#### Scenario: Tour with three dates

- **WHEN** an operator opens XX Tour 2026 with events on 3, 10 and 17 November
- **THEN** the three events are listed in that order with their venues and states, and selecting 3 November opens its event page

#### Scenario: Unknown concert

- **WHEN** an operator opens a concert address whose concert is not among the Organizer's concerts
- **THEN** the page says the concert was not found and links to Concerts

### Requirement: Share link of an unlisted concert

For a published UNLISTED concert the page SHALL explain that fans can open it only through its share link and offer 新しい共有リンクを発行 (create a new share link). Because an existing link is never shown again, creating one SHALL first ask for confirmation saying that the previous link stops working; after confirmation the page SHALL show the new link with a copy action. A PUBLIC or draft concert SHALL not offer a share link.

#### Scenario: New share link

- **WHEN** an operator confirms 新しい共有リンクを発行 on a published UNLISTED concert
- **THEN** the page shows the new link with a copy action and the previous link no longer opens the concert

#### Scenario: Public concert

- **WHEN** an operator opens a published PUBLIC concert
- **THEN** no share link action is offered
