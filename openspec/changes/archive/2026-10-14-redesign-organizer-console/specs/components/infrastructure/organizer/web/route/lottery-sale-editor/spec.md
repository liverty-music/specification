# Spec Delta

## ADDED Requirements

### Requirement: Opened from the event's Sales tab and back

The lottery sale editor SHALL be opened from 抽選で販売する on an event's Sales tab, or from 編集 on one of the event's lottery sales, SHALL show that event's date, start time and venue, and SHALL have the event as its parent in the breadcrumb. After the sale is created or changed the console SHALL return to the event's Sales tab; leaving without saving SHALL return there too, guarding unsaved changes.

#### Scenario: Back after creating

- **WHEN** an operator creates a lottery sale from the Sales tab of the 3 November event
- **THEN** the Sales tab of the 3 November event opens and lists the new sale

#### Scenario: Breadcrumb

- **WHEN** the editor is open for the 3 November event of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火) › 抽選で販売

### Requirement: The window is entered in Japan time

The editor SHALL take the sale's start and end as Japan time, marked JST, whatever the device's time zone, and SHALL show the price with yen separators.

#### Scenario: Device in another time zone

- **WHEN** an operator whose device is set to London time enters a start of 2026-10-10 12:00 JST and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October

### Requirement: A lottery sale changes only before it opens

Opened with 編集 for a lottery sale, the editor SHALL show the sale's name without letting it change, and SHALL let the operator change the window, the price, the quantity and the per-account limit under the same rules as a new sale. It SHALL save the window with TicketSaleService.SetWindow and the price, quantity and per-account limit with TicketTypeService.Update. When the sale has opened by the time the operator saves, the editor SHALL say that a lottery cannot change once its window has opened and SHALL save nothing.

#### Scenario: Move the window before it opens

- **WHEN** an operator moves an unopened lottery's window from 10 to 17 October to 12 to 19 October and saves
- **THEN** the sale opens on 12 October and the Sales tab shows the new window

#### Scenario: Change the price before it opens

- **WHEN** an operator changes an unopened lottery's price from 8000 to 7500 yen and saves
- **THEN** the sale's TicketType costs 7500 yen

#### Scenario: Sale opened while editing

- **WHEN** an operator saves a change after the lottery's window has opened
- **THEN** the editor says the lottery cannot change once its window has opened and nothing is saved
