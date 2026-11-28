## Purpose

Records that a registered artist's MBID could not be verified automatically because several catalog artists share its name, so an admin decides which one it is.

## ADDED Requirements

### Requirement: MarkMBIDAmbiguous sets the status and nothing else
MarkMBIDAmbiguous SHALL set the mbid_status of the artist with the given id to Ambiguous and change nothing else. It SHALL fail with NotFound when no artist has the id. Calling it for an artist already Ambiguous SHALL succeed and change nothing. It SHALL announce nothing.

#### Scenario: Unverified artist
- **WHEN** MarkMBIDAmbiguous is called for an Unverified artist
- **THEN** its mbid_status is Ambiguous and its mbid, listening_mbid and name are unchanged

#### Scenario: Already ambiguous
- **WHEN** MarkMBIDAmbiguous is called for an artist whose mbid_status is Ambiguous
- **THEN** it succeeds and nothing changes

#### Scenario: Unknown artist
- **WHEN** MarkMBIDAmbiguous is called with an id no artist has
- **THEN** it fails with NotFound
