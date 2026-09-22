# Auth Headers

## Purpose

Establish comprehensive test coverage for the Aurelia 2 frontend application, including test infrastructure, service tests, component tests, and coverage reporting.

This capability ensures code quality, prevents regressions, and enables confident refactoring through automated testing.

## Requirements

### Requirement: gRPC transport injects auth headers
The `authInterceptor` within `createTransport` SHALL inject a Bearer token into every outgoing gRPC request.

#### Scenario: Authenticated user has valid token
- **WHEN** the current authentication session yields a user with an `access_token`
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` to the request headers

#### Scenario: No authenticated user
- **WHEN** the current authentication session yields no user (`null`)
- **THEN** the interceptor SHALL NOT add an Authorization header
