# components/infrastructure/organizer/web/global/i18n Specification

## Purpose
How the organizer console chooses its language and shows dates, times and prices: Japanese or English text, every date and time in the time zone it belongs to and labelled with that zone, and yen amounts with separators, whatever the device's own language or time zone.

## Requirements

### Requirement: Japanese or English, chosen on the device

Every label, message and error the console shows SHALL come in Japanese and in English. On first open the console SHALL use the language saved on this device; when none is saved it SHALL use Japanese when the browser's preferred language is Japanese and English otherwise. A member SHALL be able to switch the language from the account menu; the switch SHALL change every text on the page at once without a reload and SHALL be saved on this device only. The page's declared language SHALL always match the language shown, so that screen readers and the browser's text handling follow it.

#### Scenario: First open on a Japanese browser

- **WHEN** a member opens the console for the first time in a browser whose preferred language is Japanese
- **THEN** the console is in Japanese and the page declares Japanese

#### Scenario: Browser in another language

- **WHEN** a member opens the console for the first time in a browser whose preferred language is French
- **THEN** the console is in English and the page declares English

#### Scenario: Member switches to English

- **WHEN** a member switches the language to English from the account menu
- **THEN** every text on the page changes to English without a reload, the page declares English, and the next visit on this device opens in English

#### Scenario: Every text follows a switch

- **WHEN** a member on Settings switches from English to Japanese, and then opens the concert editor
- **THEN** the business detail labels, the account menu's mark on the chosen language, the concert type choices and every option list are in Japanese

### Requirement: Prices in yen with separators

Every price the console shows SHALL be in yen with digit separators and no decimal places, formatted for the current language (for example `6,500円` in Japanese and `¥6,500` in English). Counts of tickets and entries SHALL also show digit separators.

#### Scenario: Ticket price

- **WHEN** a SeatType's price is 6500 yen and the console is in Japanese
- **THEN** the price is shown as 6,500円

#### Scenario: Large count

- **WHEN** a sale has 1380 requested tickets
- **THEN** the count is shown as 1,380

### Requirement: Sign-in opens in the console's language

Every redirect from the console to the hosted login screen (the sign-in started when a member opens the console without a session, and the sign-in started after an involuntary logout) SHALL ask the hosted login to show the language the console is showing at that moment.

#### Scenario: Member who chose Japanese on an English browser

- **WHEN** a member who switched the console to Japanese on a browser whose preferred language is English opens the console without a session
- **THEN** the hosted login screen opens in Japanese

#### Scenario: Member who chose English on a Japanese browser

- **WHEN** a member who switched the console to English on a browser whose preferred language is Japanese is logged out because the session can no longer be renewed
- **THEN** the hosted login screen opens in English

### Requirement: Dates and times in the zone they belong to

Every date and time the console shows SHALL be in the time zone it belongs to, whatever the device's time zone, formatted for the current language, and labelled with that zone's name in the current language (the zone's city name as Unicode CLDR gives it: ロンドン, ソウル, 台北; Asia/Tokyo is named 日本 in Japanese and Japan in English), followed by 時間 in Japanese and `time` in English:

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
