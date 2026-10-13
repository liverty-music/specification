# Spec Delta

## ADDED Requirements

### Requirement: Publish while a concert has draft dates

The concert list SHALL show each concert's derived publish state and SHALL offer Publish for a concert whenever it has at least one DRAFT event, published or not; Publish SHALL publish every DRAFT event of the concert. Cancel SHALL be offered while the concert has a PUBLISHED or DRAFT event.

#### Scenario: Published tour with a new date
- **WHEN** a PUBLISHED concert has one DRAFT event
- **THEN** the list shows the concert as Published and offers Publish, which publishes the DRAFT event

#### Scenario: Nothing left to publish
- **WHEN** every event of a concert is PUBLISHED or CANCELLED
- **THEN** Publish is not offered
