# Auth Status

## Purpose

Establish comprehensive test coverage for the Aurelia 2 frontend application, including test infrastructure, service tests, component tests, and coverage reporting.

This capability ensures code quality, prevents regressions, and enables confident refactoring through automated testing.

## Requirements

### Requirement: Auth status delegates to auth service
The auth status surface SHALL delegate sign-in, sign-up, and sign-out actions to the auth service.

#### Scenario: Sign in
- **WHEN** `signIn` is called
- **THEN** it SHALL call `auth.signIn()`

#### Scenario: Sign up
- **WHEN** `signUp` is called
- **THEN** it SHALL call `auth.signUp()`

#### Scenario: Sign out
- **WHEN** `signOut` is called
- **THEN** it SHALL call `auth.signOut()`
