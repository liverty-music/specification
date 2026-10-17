# components/infrastructure/organizer/web/global/i18n Specification

## Purpose
How the organizer console chooses its language and shows dates, times and prices: Japanese or English text, every date and time in Japan time marked JST, and yen amounts with separators, whatever the device's own language or time zone.

## Requirements

### Requirement: Japanese or English, chosen on the device

Every label, message and error the console shows SHALL come in Japanese and in English. On first open the console SHALL use the language saved on this device; when none is saved it SHALL use English when the browser's preferred language is English and Japanese otherwise. A member SHALL be able to switch the language from the account menu; the switch SHALL change every text on the page at once without a reload and SHALL be saved on this device only. The page's declared language SHALL always match the language shown, so that screen readers and the browser's text handling follow it.

#### Scenario: First open on a Japanese browser

- **WHEN** a member opens the console for the first time in a browser whose preferred language is Japanese
- **THEN** the console is in Japanese and the page declares Japanese

#### Scenario: Browser in another language

- **WHEN** a member opens the console for the first time in a browser whose preferred language is French
- **THEN** the console is in Japanese

#### Scenario: Member switches to English

- **WHEN** a member switches the language to English from the account menu
- **THEN** every text on the page changes to English without a reload, the page declares English, and the next visit on this device opens in English

#### Scenario: Every text follows a switch

- **WHEN** a member on Settings switches from English to Japanese, and then opens the concert editor
- **THEN** the business detail labels, the account menu's mark on the chosen language, the concert type choices and every option list are in Japanese

### Requirement: Dates and times in Japan time

Every date and time the console shows SHALL be in Japan time (Asia/Tokyo) with the label JST, whatever the device's time zone, and formatted for the current language (for example `11月3日(火) 18:00 JST` in Japanese and `Tue, Nov 3, 18:00 JST` in English). Every date and time a member enters SHALL be read as Japan time, and the field SHALL say JST next to it. Every time a member enters, in any console editor, SHALL be entered as an hour from 00 to 23 and a minute in steps of 5, with no AM or PM, whatever the device's clock setting.

#### Scenario: Member abroad

- **WHEN** a member whose device is set to London time opens an event that starts at 18:00 in Tokyo
- **THEN** the page shows 18:00 JST

#### Scenario: Entering a sale window abroad

- **WHEN** a member whose device is set to London time enters a sale start of 2026-10-10 12:00 in a field marked JST
- **THEN** the sale starts at 12:00 Japan time, not 12:00 London time

#### Scenario: Device on a 12-hour clock

- **WHEN** a member whose device shows times as 6:00 PM opens a sale window field
- **THEN** the field offers hours 00 to 23 and minutes in steps of 5, with no AM or PM

### Requirement: Prices in yen with separators

Every price the console shows SHALL be in yen with digit separators and no decimal places, formatted for the current language (for example `6,500円` in Japanese and `¥6,500` in English). Counts of tickets and entries SHALL also show digit separators.

#### Scenario: Ticket price

- **WHEN** a TicketType's price is 6500 yen and the console is in Japanese
- **THEN** the price is shown as 6,500円

#### Scenario: Large count

- **WHEN** a sale has 1380 requested tickets
- **THEN** the count is shown as 1,380
