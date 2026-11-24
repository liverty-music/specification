## ADDED Requirements

### Requirement: A sale's window is entered in the sale's time zone

The editor SHALL show the sale's time zone, by its name. When the venues of the events the sale names share one time zone (the usual case, a sale of one event), the zone SHALL be that zone, shown as read-only text. When those venues are in different zones, the zone SHALL be a select of their zones, preselected with the sale's zone for an existing sale and with none for a new sale. The sale's start and end SHALL be entered as wall-clock date and times in that zone, whatever the device's time zone, and each field SHALL show the zone's name. Saving SHALL send the window with that zone. The editor SHALL NOT save while no zone is selected, and SHALL show an error next to a time that does not exist in the zone, because the clocks move forward then. When saving is refused because the zone is not one of the zones of the events' venues, the screen SHALL say so next to the zone and nothing is saved. The seat types' prices SHALL be shown with yen separators.

#### Scenario: Event in Japan

- **WHEN** a member opens the editor for a new sale of an event at a Venue in Tokyo
- **THEN** the time zone shows 日本 as text with no select, and the start and end fields are marked 日本時間

#### Scenario: Event abroad

- **WHEN** a member opens the editor for a new sale of an event at a Venue in Taipei and enters a start of 2027-02-01 12:00
- **THEN** the time zone shows 台北 as text, and the sale opens at 12:00 Taipei time on 1 February

#### Scenario: Events at venues in different zones

- **WHEN** a member opens the editor for a new sale whose events are at a Venue in Tokyo and a Venue in Taipei
- **THEN** the time zone is a select of 日本 and 台北 with none selected, and saving says a time zone must be chosen until one is

#### Scenario: Device in another time zone

- **WHEN** a member whose device is set to London time enters a start of 2026-10-10 12:00 for a sale whose time zone is Asia/Tokyo and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October

#### Scenario: Time skipped by the clocks moving forward

- **WHEN** a member enters a start of 2027-03-14 02:30 for a sale whose time zone is America/New_York and saves
- **THEN** an error is shown next to the start and nothing is saved

## MODIFIED Requirements

### Requirement: A first-come sale's settings and defaults

For an event without a first-come sale, the screen SHALL offer the sale's name and the start time and end time, entered in the sale's time zone, with the name defaulting to 一般発売 and the end time defaulting to the event's start time in that zone. It SHALL list the event's TicketStocks the sale will sell, each with its seat type's name and price 税込 (tax-inclusive) and its quantity, and SHALL say that the sale sells every seat type of the event and that the per-account limit is the event's, with that limit. Saving SHALL create a FirstCome sale of the event's Series naming the event, with TicketSaleService.Create. It SHALL show an error next to a field, without saving, when the end time is after the event's start time, the end is not after the start, or the name is empty or longer than 100 characters. When saving fails because the window overlaps another sale of the event, the screen SHALL say so.

#### Scenario: Blank form

- **WHEN** a member opens the editor for an event starting 2026-11-20 19:00 at a Venue in Tokyo with the TicketStocks S席 8,000円 × 300 and A席 6,000円 × 700 and a per-account limit of 4
- **THEN** the end time is 2026-11-20 19:00 日本時間, the name is 一般発売, and the screen lists S席 and A席 and says up to 4 tickets per account

#### Scenario: End after the show starts

- **WHEN** the member sets the end time to 19:30 for a 19:00 show and saves
- **THEN** an error is shown next to the end time and nothing is saved

#### Scenario: Overlapping a presale

- **WHEN** the event's lottery presale runs to 10 November and the member saves a sale starting 8 November
- **THEN** the screen says the window overlaps another sale and nothing is saved

## REMOVED Requirements

### Requirement: A lottery window is entered in Japan time

**Reason**: A sale has its own time zone, which defaults to the zone of its events' venues; the window of a lottery or first-come sale is entered in that zone. See "A sale's window is entered in the sale's time zone".
**Migration**: Every Organizer sale today gets the time zone Asia/Tokyo, so a window entered as JST keeps its wall-clock times.
