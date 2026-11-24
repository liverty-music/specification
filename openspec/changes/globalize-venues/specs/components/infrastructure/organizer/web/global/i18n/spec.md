## ADDED Requirements

### Requirement: Dates and times in the zone they belong to

Every date and time the console shows SHALL be in the time zone it belongs to, whatever the device's time zone, formatted for the current language, and labelled with that zone's name as the API returns it in the current language (the city name of the zone: ロンドン, ソウル, 台北; Asia/Tokyo is named 日本 in Japanese and Japan in English), followed by 時間 in Japanese and `time` in English:

| time | shown in | label |
|---|---|---|
| an Event's date, open time and start time | the local time of the event's Venue | the Venue zone's name; when the zone is not Asia/Tokyo, the time in Japan time in parentheses, with its date when it falls on another date |
| a TicketSale's start and end | the sale's time zone | the sale zone's name |
| a moment in the past about an event (a Scanner first opened) | the time zone of the event's Venue | the Venue zone's name |

For example, an event at a Venue in Tokyo is shown as `11月3日(火) 18:00 日本時間`, and an event at a Venue in London as `2月20日(土) 19:30 ロンドン時間（日本時間 2月21日(日) 04:30）` in Japanese and `Sat, Feb 20, 19:30 London time (Japan time Feb 21, 04:30)` in English. A date shown without a time is the date at the event's Venue and carries no label.

Every date and time a member enters SHALL be read in the time zone the field names, and the field SHALL show that zone's name next to it: an Event's times in the zone of the event's Venue, a TicketSale's window in the sale's time zone. Every time a member enters, in any console editor, SHALL be entered as an hour from 00 to 23 and a minute in steps of 5, with no AM or PM, whatever the device's clock setting.

#### Scenario: Member abroad

- **WHEN** a member whose device is set to London time opens an event that starts at 18:00 at a Venue in Tokyo
- **THEN** the page shows 18:00 日本時間

#### Scenario: Event abroad

- **WHEN** a member whose device is set to Japan time opens an event that starts on 2027-02-20 at 19:30 at a Venue in London
- **THEN** the page shows 2月20日(土) 19:30 ロンドン時間（日本時間 2月21日(日) 04:30）

#### Scenario: Event in another zone with Japan's offset

- **WHEN** a member opens an event that starts at 18:30 at a Venue in Seoul
- **THEN** the page shows 18:30 ソウル時間（日本時間 18:30）

#### Scenario: Sale window in its own zone

- **WHEN** a member whose device is set to Japan time opens a TicketSale in the time zone Asia/Taipei that opens on 2027-02-01 at 12:00
- **THEN** the page shows the start as 2月1日(月) 12:00 台北時間, with no Japan time

#### Scenario: Scanner opened abroad

- **WHEN** venue staff first open a Scanner of an event at a Venue in London at 18:05 London time
- **THEN** the console shows that moment as 18:05 ロンドン時間, whatever the member's device time zone

#### Scenario: Entering a sale window abroad

- **WHEN** a member whose device is set to London time enters a sale start of 2026-10-10 12:00 in a field marked 日本時間 for a sale in Asia/Tokyo
- **THEN** the sale starts at 12:00 Japan time, not 12:00 London time

#### Scenario: Device on a 12-hour clock

- **WHEN** a member whose device shows times as 6:00 PM opens a sale window field
- **THEN** the field offers hours 00 to 23 and minutes in steps of 5, with no AM or PM

## REMOVED Requirements

### Requirement: Dates and times in Japan time

**Reason**: Venues outside Japan have their own time zones. Times are now shown and entered in the zone they belong to (Event times at the Venue's local time, a sale's window in the sale's time zone), each labelled with that zone's name; see "Dates and times in the zone they belong to".
**Migration**: Existing Event and sale times are converted to wall-clock times in their Venue's or sale's zone (Asia/Tokyo for every Organizer event and sale today), so every time the console showed as JST is shown with the same digits and the label 日本時間.
