# Entity Test Coverage Specification

## Purpose

Defines the required unit-test coverage for frontend entity mapping and helper functions.

## Requirements

### Requirement: Error code semantic correctness
Infrastructure implementations SHALL use `apperr` codes according to gRPC code semantics.

#### Scenario: JSON decode failure
- **WHEN** an external API response fails JSON decoding
- **THEN** the implementation SHALL return `codes.Internal` (not `codes.DataLoss`, which means unrecoverable data loss or corruption)

#### Scenario: Input validation failure
- **WHEN** a function receives invalid input (empty ID, malformed URL, unsupported type)
- **THEN** the implementation SHALL return `codes.InvalidArgument`

#### Scenario: External service unreachable
- **WHEN** an external service is down, rate-limited, or all retries are exhausted
- **THEN** the implementation SHALL return `codes.Unavailable`
