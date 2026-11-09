# Spec Delta

## MODIFIED Requirements

### Requirement: A new artist starts without images
A new Artist SHALL get a fresh unique id and SHALL start with no fanart, no fanart_sync_time, no official_site_check_time and activity_ended false.

#### Scenario: New artist
- **WHEN** an artist is created from a name and an MBID
- **THEN** it has a fresh id, that name and MBID, no fanart, no fanart_sync_time, no official_site_check_time and activity_ended false

#### Scenario: Two new artists
- **WHEN** two artists are created from the same name and MBID
- **THEN** their ids differ
