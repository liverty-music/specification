<!-- spec: entity-domain-logic | target: components/entity/concert | flags: CLASSNAME | new_name: Discovered-concert to Concert conversion -->

### Requirement: ScrapedConcert to Concert conversion

The `ScrapedConcert` entity SHALL provide a `ToConcert(artistID, eventID, venueID string) *Concert` method that constructs a `Concert` from the scraped data.

The method SHALL map fields as follows:
- `Concert.ID` = `eventID`
- `Concert.ArtistID` = `artistID`
- `Concert.VenueID` = `venueID`
- `Concert.Title` = `ScrapedConcert.Title`
- `Concert.LocalDate` = `ScrapedConcert.LocalDate`
- `Concert.StartTime` = `ScrapedConcert.StartTime`
- `Concert.URL` = `ScrapedConcert.URL`

#### Scenario: Full field mapping

- **WHEN** ToConcert is called on a ScrapedConcert with all fields populated
- **THEN** the returned Concert has ID=eventID, ArtistID=artistID, VenueID=venueID, and all other fields copied from the ScrapedConcert

#### Scenario: Nil optional fields

- **WHEN** ToConcert is called on a ScrapedConcert where StartTime and URL are nil
- **THEN** the returned Concert has nil StartTime and nil URL

#### Scenario: Multiple calls produce distinct concerts

- **WHEN** ToConcert is called twice with different artistID/eventID/venueID values on the same ScrapedConcert
- **THEN** each call returns a distinct Concert with the respective IDs

---
