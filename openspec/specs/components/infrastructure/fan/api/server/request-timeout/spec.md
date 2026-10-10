# Request Timeout

## Purpose

A server-wide limit on how long the fan API works on one call before giving up.

## Requirements

### Requirement: Every fan call gets 30 seconds

Every call to any service of the fan API SHALL be given up after 30 seconds. A call that is given up SHALL fail with Unavailable, and the caller receives no partial result.

#### Scenario: Concert call over the limit

- **WHEN** a concert call is still running after 30 seconds
- **THEN** the caller receives Unavailable

#### Scenario: Other call over the limit

- **WHEN** a follow call is still running after 30 seconds
- **THEN** the caller receives Unavailable
