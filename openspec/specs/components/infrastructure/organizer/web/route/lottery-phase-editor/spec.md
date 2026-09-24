# Lottery Phase Editor

## Purpose

The organizer console screen where an operator puts one published event on sale by lottery: the application window, the ticket capacity, the per-application limit and the price.

## Requirements

### Requirement: The application window defaults to 10 days

A new lottery phase form SHALL open with the window starting now and closing 10 days later. The screen SHALL accept a window of 1 to 14 days and SHALL show an error next to the window, without saving, for any other length.

#### Scenario: Blank form

- **WHEN** an operator opens the lottery phase editor for an event without a phase at 2026-10-01 12:00
- **THEN** the window opens at 2026-10-01 12:00 and closes at 2026-10-11 12:00

#### Scenario: Window too long

- **WHEN** the operator sets a window of 15 days and saves
- **THEN** an error is shown next to the window and nothing is saved
