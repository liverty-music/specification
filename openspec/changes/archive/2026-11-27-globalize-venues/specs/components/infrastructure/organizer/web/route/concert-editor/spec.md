## ADDED Requirements

### Requirement: The member confirms the name, country, area and time zone of a new venue

After the member picks a place, the venue field SHALL read it with VenueService.ResolvePlace.

When the place is already a Venue, the field SHALL show that Venue's name, its area by name in the member's language and its time zone by name as text, and offer no input for them.

Otherwise the field SHALL show four inputs, prefilled from the place, each of which the member may change:

- 会場名 (venue name): the place's name; required.
- 国 (country): a select of the countries read with AreaService.ListCountries, each by its name in the member's language, preselected with the place's country.
- 地域 (area): the first-level Areas of the chosen country, read with AreaService.ListByCountry, by name in the member's language and grouped under the country's regions (関東, 近畿 and so on for Japan; one ungrouped list for a country without regions); preselected with the area the place's address suggests, or with none when there is no suggestion; required.
- タイムゾーン (time zone): always shown. When the chosen country has more than one time zone, a select of the country's zones, each by name and its current offset from UTC (`ロサンゼルス (UTC−8)`), preselected with the place's zone, or with none when there is no zone; when the country has one zone, that zone's name as read-only text. Required.

Choosing another 国 SHALL replace the 地域 list and the タイムゾーン choices with that country's, clear the 地域 selection, and select the country's zone when it has only one, or clear the selection otherwise. Choosing an Area that lies wholly in one time zone SHALL select that zone. Saving SHALL send the 会場名, area and time zone the member left in the field, never the place's own values unseen by the member. The editor SHALL NOT save while a new venue has an empty 会場名, no area or no time zone; the field in error SHALL say what must be filled in. When the place, the countries, or the country's areas and zones cannot be read, the field SHALL say so and offer 再試行, and the event has no venue.

#### Scenario: Place in Japan prefilled

- **WHEN** a member picks Zepp Haneda (TOKYO), which no Venue holds
- **THEN** 会場名 shows Zepp Haneda (TOKYO), 国 shows 日本, 地域 lists the 47 prefectures grouped under the eight regions with 東京都 selected, and タイムゾーン shows 日本 as text

#### Scenario: Place abroad prefilled

- **WHEN** a member picks Gocheok Sky Dome, which no Venue holds
- **THEN** 国 shows 韓国, 地域 shows ソウル特別市 selected, and タイムゾーン shows ソウル as text

#### Scenario: Country with several time zones

- **WHEN** a member picks a place in Los Angeles that no Venue holds
- **THEN** 地域 shows カリフォルニア州 selected, and タイムゾーン is a select of the United States' zones with ロサンゼルス (UTC−8) selected

#### Scenario: Member renames the venue and changes the area

- **WHEN** the member changes 会場名 to Zepp Haneda, selects 神奈川県 instead of 東京都 and saves
- **THEN** the event's new Venue is saved with the name Zepp Haneda, the area JP-14 and the time zone Asia/Tokyo

#### Scenario: Member changes the country

- **WHEN** the member changes 国 from 日本 to 韓国
- **THEN** 地域 lists the first-level Areas of South Korea with none selected, and タイムゾーン shows ソウル as text

#### Scenario: No suggested area

- **WHEN** the picked place has no suggested area
- **THEN** 地域 has none selected, and saving says an area must be chosen until one is

#### Scenario: Several zones and none suggested

- **WHEN** the picked place is in a country with more than one zone and the place has no zone
- **THEN** タイムゾーン has none selected, and saving says a time zone must be chosen until one is

#### Scenario: Place already a Venue

- **WHEN** a member picks a place that a Venue named Zepp Namba (OSAKA) in JP-27 holds
- **THEN** the field shows Zepp Namba (OSAKA), 大阪府 and 日本 as text, and no 会場名, 国, 地域 or タイムゾーン input

#### Scenario: Place cannot be read

- **WHEN** the place cannot be read after the member picks it
- **THEN** the field says the place cannot be read and offers 再試行, and the event has no venue

### Requirement: Event times are entered at the venue's local time on a 24-hour clock

The editor SHALL take each event's date, open time and start time as the wall-clock date and times at the event's venue, whatever the device's time zone or language. Each time SHALL be entered as an hour from 00 to 23 and a minute in steps of 5, with no AM or PM. After its times, each date row SHALL show the name of its venue's time zone followed by 時間 (`ソウル時間`), and, when that zone is not Asia/Tokyo, the start time in Japan time in parentheses, with its date when it falls on another date. A row whose venue has no time zone yet SHALL show no zone. Changing a row's venue or time zone SHALL keep the entered date and times and update the zone's name and the Japan time. A time that does not exist at the venue on that date, because the clocks move forward then, SHALL be shown as an error next to the time, and nothing is saved. A new concert's first date SHALL start with 開場 (doors) 17:00 and 開演 (start) 19:00. Adding a date SHALL copy the previous date's venue, date, open time and start time into the new one.

#### Scenario: Venue in Japan

- **WHEN** a member enters 開演 18:00 for a date at Zepp Haneda
- **THEN** the row shows 日本時間 after the times and no Japan time in parentheses

#### Scenario: Venue abroad

- **WHEN** a member enters 開場 17:30 and 開演 18:30 on 2027-03-14 for a date at Gocheok Sky Dome in Seoul
- **THEN** the row shows ソウル時間 (日本時間 18:30) after the times

#### Scenario: Japan time on another date

- **WHEN** a member enters 開演 19:30 on 2027-02-20 for a date at a venue in London
- **THEN** the row shows ロンドン時間 (日本時間 2月21日(日) 04:30) after the times

#### Scenario: Device in another time zone

- **WHEN** a member whose device is set to London time enters a start time of 18:00 for a date at a venue in Tokyo and saves
- **THEN** the event starts at 18:00 Japan time, and reopening the editor shows 18:00 日本時間

#### Scenario: Time skipped by the clocks moving forward

- **WHEN** a member enters 開演 02:30 on 2027-03-14 for a date at a venue in New York and saves
- **THEN** an error next to the start time says the time does not exist at the venue on that date, and nothing is saved

#### Scenario: Device using a 12-hour clock

- **WHEN** a member whose device shows times as 6:00 PM opens the editor
- **THEN** the time fields show hours 00 to 23 and no AM or PM

#### Scenario: Defaults of a new concert

- **WHEN** a member creates a concert
- **THEN** its first date shows 開場 17:00 and 開演 19:00

#### Scenario: Another night at the same venue

- **WHEN** a date at Zepp Haneda on 3 November with 開場 17:00 and 開演 18:00 is followed by 日程を追加
- **THEN** the new date shows Zepp Haneda, 3 November, 17:00 and 18:00, ready to change the date

## REMOVED Requirements

### Requirement: Event times are entered in Japan time on a 24-hour clock

**Reason**: A venue outside Japan has its own time zone, and an event's times are the wall-clock times at its venue; see "Event times are entered at the venue's local time on a 24-hour clock".
**Migration**: Every Organizer event today is at a venue in Asia/Tokyo, so the times entered as JST are the same wall-clock times at the venue.
