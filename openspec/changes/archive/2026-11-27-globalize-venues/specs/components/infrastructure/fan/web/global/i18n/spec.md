## ADDED Requirements

### Requirement: Each kind of time is shown in the zone it belongs to

Every date and time the fan app shows SHALL be formatted for the display language in the time zone its kind belongs to, whatever the zone a page or screen is opened from:

| time | shown in | label |
|---|---|---|
| an Event's date, open time and start time; a resale draw and the resale deadline of an Event | the local time of the event's Venue | when the browser's time zone has another offset from UTC than the Venue's zone at that moment: the Venue zone's name, and in parentheses the browser zone's name and the time there, with its date when it falls on another date; otherwise none |
| a TicketSale's start and end | the browser's time zone | when the browser's time zone is not the sale's time zone: the browser zone's name; otherwise none |
| a moment in the past (an admission, a passkey's creation, a refund) | the browser's time zone | none |

The name of a time zone, whether a Venue's, a sale's or the browser's own, SHALL be the zone's city name in the display language as Unicode CLDR gives it (ロンドン, 台北; London, Taipei), except Asia/Tokyo, which is named 日本 in Japanese and Japan in English. The app SHALL name a zone from the IANA name alone, without asking the server for a name. Every zone name SHALL be followed by 時間 in Japanese and `time` in English. When several times of one Event are shown together, the Venue zone's name SHALL be shown once after them, followed by the browser zone's times in the same order. A date shown without a time is the date at the event's Venue and carries no label. Notification texts are not screens and keep their own rule.

#### Scenario: Event and fan in Japan

- **WHEN** a fan whose browser is set to Japan time opens an event that starts at 18:00 at a Venue in Tokyo
- **THEN** the start is shown as 18:00 with no zone

#### Scenario: Event abroad seen from Japan

- **WHEN** a fan whose browser is set to Japan time opens an event that starts on 2027-02-20 at 19:30 at a Venue in London
- **THEN** the start is shown as 2月20日(土) 19:30 ロンドン時間（日本時間 2月21日(日) 04:30）

#### Scenario: Event in Japan seen from abroad

- **WHEN** a fan whose browser is set to London time opens an event that starts on 2026-11-03 at 18:00 at a Venue in Tokyo
- **THEN** the start is shown as 11月3日(火) 18:00 日本時間（ロンドン時間 09:00）

#### Scenario: Event in Taipei seen from Japan

- **WHEN** a fan whose browser is set to Japan time opens an event that starts at 19:00 at a Venue in Taipei
- **THEN** the start is shown as 19:00 台北時間（日本時間 20:00）

#### Scenario: Another zone with the same offset

- **WHEN** a fan whose browser is set to Japan time opens an event that starts at 18:30 at a Venue in Seoul
- **THEN** the start is shown as 18:30 with no zone, because Seoul and Japan have the same offset at that moment

#### Scenario: English display language

- **WHEN** the display language is English and a fan whose browser is set to Japan time opens an event that starts on 2027-02-20 at 19:30 at a Venue in London
- **THEN** the start is shown as Sat, Feb 20, 19:30 London time (Japan time Feb 21, 04:30)

#### Scenario: Sale abroad seen from Japan

- **WHEN** a fan whose browser is set to Japan time sees a TicketSale in the time zone Asia/Taipei that opens on 2027-02-01 at 12:00
- **THEN** the start is shown as 2月1日(月) 13:00 日本時間

#### Scenario: Sale in the fan's own zone

- **WHEN** a fan whose browser is set to Japan time sees a TicketSale in the time zone Asia/Tokyo that opens on 2026-11-01 at 10:00
- **THEN** the start is shown as 11月1日(日) 10:00 with no zone

#### Scenario: Resale deadline abroad

- **WHEN** a fan whose browser is set to Japan time sees the resale deadline of an event at a Venue in London, which is 2027-02-20 12:00 London time
- **THEN** the deadline is shown as 2月20日(土) 12:00 ロンドン時間（日本時間 21:00）

#### Scenario: Admission time

- **WHEN** a fan whose browser is set to Japan time was admitted at an event in London at 18:10 London time on 2027-02-20
- **THEN** the admission time is shown as 2月21日(日) 03:10 with no zone
