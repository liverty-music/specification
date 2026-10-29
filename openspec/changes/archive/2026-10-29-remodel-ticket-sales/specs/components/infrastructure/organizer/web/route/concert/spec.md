# Spec Delta

## ADDED Requirements

### Requirement: The concert's seat types

The page SHALL show a section 席種 (seat types) listing the concert's SeatTypes, read with SeatTypeService.ListBySeries, each with its name and price 税込 (tax-inclusive), and SHALL say that every date of the concert sells from these seat types and that the quantity of each is set on each date's Sales tab. It SHALL offer 席種を追加 (add a seat type), which asks for a name of 1 to 50 characters and a price of 1 to 1,000,000 yen and creates the SeatType with SeatTypeService.Create after a confirmation saying that the name and price cannot be changed afterwards. A SeatType that no date stocks SHALL offer 削除 (delete), which deletes it with SeatTypeService.Delete after confirmation; one that a date stocks SHALL offer no delete. A name already used by another seat type of the concert SHALL be shown as an error next to the name, and nothing is saved. A concert whose dates are all cancelled SHALL offer neither action.

#### Scenario: Dome tour seat types

- **WHEN** a member adds S席 at 12,000 yen, A席 at 9,000 yen and B席 at 7,000 yen to XX Dome Tour 2026
- **THEN** the section lists the three seat types with 12,000円, 9,000円 and 7,000円, and says the quantities are set on each date

#### Scenario: Price mistake before stocking

- **WHEN** a member added S席 at 1,200 yen by mistake and no date stocks it
- **THEN** S席 offers 削除, and after deleting it the member adds S席 at 12,000 yen

#### Scenario: Seat type in use

- **WHEN** the 3 November date stocks S席
- **THEN** S席 offers no delete and no way to change its name or price

#### Scenario: Name already used

- **WHEN** the concert has S席 and the member adds another seat type named S席
- **THEN** an error is shown next to the name and nothing is saved
