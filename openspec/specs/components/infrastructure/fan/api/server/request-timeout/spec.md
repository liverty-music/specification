# Request Timeout

## Purpose

A server-wide limit on how long the fan API works on one call before giving up, with a longer limit for concert calls because a concert search can take close to two minutes.

## Requirements

### Requirement: Concert calls get 120 seconds, every other call 30 seconds

Every call to the concert service SHALL be given up after 120 seconds; every call to any other service of the fan API SHALL be given up after 30 seconds. A call that is given up SHALL fail with Unavailable, and the caller receives no partial result.

#### Scenario: Long concert search

- **WHEN** a SearchNewConcerts call takes 90 seconds
- **THEN** it completes and its result is returned

#### Scenario: Concert call over the limit

- **WHEN** a concert call is still running after 120 seconds
- **THEN** the caller receives Unavailable

#### Scenario: Other call over the limit

- **WHEN** a follow call is still running after 30 seconds
- **THEN** the caller receives Unavailable
