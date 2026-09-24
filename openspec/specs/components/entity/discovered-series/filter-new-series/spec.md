# DiscoveredSeries.FilterNewSeries

## Purpose

Drops from newly DiscoveredSeries the events already known — among an Artist's existing Concerts or earlier in the same batch — keeping each series' grouping for the events that remain.

## Requirements

### Requirement: Novelty by date, venue and start time

FilterNewSeries SHALL compare events by local date and normalized listed venue name, and within the same date and venue SHALL treat start time asymmetrically:
- an event with no start time is known when anything is known at that date and venue;
- an event with a start time is known only when that exact start time is known there, so a start time announced after an unknown-start Concert is kept.

Existing Concerts without a listed venue name SHALL be ignored. Events with a blank listed venue name SHALL be dropped. Each event kept SHALL count as known for the events after it. Title, open time, source page and admin area SHALL play no part.

#### Scenario: Same instant in another time zone
- **WHEN** an existing Concert starts at 2026-06-01T09:00Z and a discovered event at the same date and venue starts at 2026-06-01T18:00+09:00
- **THEN** the event is dropped

#### Scenario: Unknown start next to a known start
- **WHEN** an existing Concert starts at 18:00 and a discovered event at the same date and venue has no start time
- **THEN** the event is dropped

#### Scenario: Start time announced later
- **WHEN** an existing Concert has no start time and a discovered event at the same date and venue starts at 18:00
- **THEN** the event is kept

#### Scenario: Matinee next to an evening show
- **WHEN** an existing Concert starts at 18:00 and a discovered event at the same date and venue starts at 13:00
- **THEN** the event is kept

#### Scenario: Venue name drift
- **WHEN** an existing Concert lists "大阪・フェスティバルホール" and a discovered event at the same date and start lists "フェスティバルホール"
- **THEN** the event is dropped

#### Scenario: Same date, different venue
- **WHEN** two discovered events share a date at different venues and nothing is known there
- **THEN** both are kept

#### Scenario: Duplicate within the batch
- **WHEN** two discovered events have the same date, venue and start time and nothing is known there
- **THEN** only the first is kept

#### Scenario: Legacy concert without listed name
- **WHEN** an existing Concert has no listed venue name
- **THEN** it drops no discovered event

### Requirement: Grouping is kept

FilterNewSeries SHALL keep each series' title, type and source page for its remaining events, keep events in their original order, and drop a series left with no events. It SHALL NOT change its input.

#### Scenario: Tour partially known
- **WHEN** a tour has three events and one is already known
- **THEN** the tour is returned with the other two events in their original order

#### Scenario: Fully known series
- **WHEN** every event of a series is known
- **THEN** the series is not returned
