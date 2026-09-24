<!-- spec: entity-domain-logic | target: components/entity/concert | flags: CLASSNAME | new_name: Discovered-concert to Concert conversion -->

### Requirement: Discovered-concert to Concert conversion

The discovered-concert entity SHALL provide a `ToConcert(artistID, eventID, venueID string) *Concert` method that constructs a `Concert` from the scraped data.

The method SHALL map fields as follows:
- `Concert.ID` = `eventID`
- `Concert.ArtistID` = `artistID`
- `Concert.VenueID` = `venueID`
- `Concert.Title` = the discovered-concert entity's `Title`
- `Concert.LocalDate` = the discovered-concert entity's `LocalDate`
- `Concert.StartTime` = the discovered-concert entity's `StartTime`
- `Concert.URL` = the discovered-concert entity's `URL`

#### Scenario: Full field mapping

- **WHEN** `ToConcert` is called on a discovered-concert entity with all fields populated
- **THEN** the returned `Concert` has ID=eventID, ArtistID=artistID, VenueID=venueID, and all other fields copied from the discovered-concert entity

#### Scenario: Nil optional fields

- **WHEN** `ToConcert` is called on a discovered-concert entity where StartTime and URL are nil
- **THEN** the returned `Concert` has nil StartTime and nil URL

#### Scenario: Multiple calls produce distinct concerts

- **WHEN** `ToConcert` is called twice with different artistID/eventID/venueID values on the same discovered-concert entity
- **THEN** each call returns a distinct `Concert` with the respective IDs
