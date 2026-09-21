# Error Mapping

## Purpose

Defines the semantics of error codes returned to the fan-facing client when a call fails, translating backend failures into a consistent, well-tested set of client-facing error codes.

## Requirements

### Requirement: Error Code Semantics and Utility Test Coverage

Infrastructure implementations SHALL use `apperr` codes according to gRPC code
semantics. The geodistance calculation utility and the API error-mapping
utility SHALL have unit test coverage.

#### Scenario: JSON decode failure
- **WHEN** an external API response fails JSON decoding
- **THEN** the implementation SHALL return `codes.Internal` (not `codes.DataLoss`, which means unrecoverable data loss or corruption)

#### Scenario: Input validation failure
- **WHEN** a function receives invalid input (empty ID, malformed URL, unsupported type)
- **THEN** the implementation SHALL return `codes.InvalidArgument`

#### Scenario: External service unreachable
- **WHEN** an external service is down, rate-limited, or all retries are exhausted
- **THEN** the implementation SHALL return `codes.Unavailable`

#### Scenario: Haversine distance calculation tested

- **WHEN** two coordinate pairs are provided
- **THEN** the Haversine function SHALL return the correct great-circle distance in kilometers
- **AND** edge cases (same point, antipodal points) SHALL be handled

#### Scenario: API error mapping tested

- **WHEN** an `apperr.Error` with a known code is passed to the error mapper
- **THEN** the corresponding HTTP status code SHALL be returned
