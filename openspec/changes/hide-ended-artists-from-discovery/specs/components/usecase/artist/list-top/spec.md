# Spec Delta

## ADDED Requirements

### Requirement: ListTop leaves out artists whose activity has ended
On every call, ArtistUseCase.ListTop SHALL read the current activity_ended of the artists it is about to return with Artist.ListByMBIDs and SHALL leave out every artist whose activity_ended is true, keeping the chart order of the rest. This SHALL apply also when the result is reused from an earlier call, so an artist whose activity_ended became true after that call is left out. The limit SHALL keep its meaning for the catalog lookup, so ListTop may return fewer artists than the limit.

#### Scenario: Chart lists an ended artist
- **WHEN** the chart for a country lists three registered artists and the second one has activity_ended true
- **THEN** ListTop returns the first and the third artist, in that order

#### Scenario: Artist marked ended after the result was reused
- **WHEN** ListTop answered a country 1 hour ago, and an artist in that answer has had activity_ended true since then
- **THEN** a second call for the same country, tag and limit returns the earlier result without that artist and without a catalog lookup

#### Scenario: Chart artist registered by this call
- **WHEN** a chart artist was not registered before this call
- **THEN** it is returned, since a new artist starts with activity_ended false
