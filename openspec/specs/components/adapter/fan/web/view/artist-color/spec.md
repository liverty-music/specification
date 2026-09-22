# Artist Color

## Purpose

Establish comprehensive test coverage for the Aurelia 2 frontend application, including test infrastructure, service tests, component tests, and coverage reporting.

This capability ensures code quality, prevents regressions, and enables confident refactoring through automated testing.

## Requirements

### Requirement: Color generator produces deterministic colors
The `artistColor` function SHALL produce a valid HSL color string deterministically from any input string.

#### Scenario: Same input produces same color
- **WHEN** `artistColor` is called twice with the same artist name
- **THEN** both calls SHALL return identical HSL color strings

#### Scenario: Different inputs produce different colors
- **WHEN** `artistColor` is called with different artist names
- **THEN** the returned HSL hue values SHALL differ

#### Scenario: Empty string input
- **WHEN** `artistColor` is called with an empty string
- **THEN** it SHALL return a valid HSL color string without throwing
