# Cancellation

## Purpose

Establish comprehensive test coverage for the Aurelia 2 frontend application, including test infrastructure, service tests, component tests, and coverage reporting.

This capability ensures code quality, prevents regressions, and enables confident refactoring through automated testing.

## Requirements

### Requirement: Concert service forwards RPC calls with AbortSignal
The `ConcertService` SHALL forward concert listing and search requests to the backend gRPC service with AbortSignal support.

#### Scenario: List concerts by artist
- **WHEN** `listConcerts` is called with an artist ID
- **THEN** it SHALL call the backend `listConcerts` RPC and return the response

#### Scenario: List concerts by follower
- **WHEN** `listByFollower` is called
- **THEN** it SHALL call the backend `listByFollower` RPC for the authenticated user

#### Scenario: AbortSignal cancels in-flight request
- **WHEN** the provided AbortSignal is aborted during a request
- **THEN** the RPC call SHALL be cancelled
