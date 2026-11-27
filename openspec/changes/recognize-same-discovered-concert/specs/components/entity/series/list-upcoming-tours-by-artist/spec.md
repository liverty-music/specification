## Purpose

Lists the discovered TOUR Series an Artist still performs in, with their titles, so that dates announced later can join their tour.

## ADDED Requirements

### Requirement: Upcoming discovered tours of an artist

ListUpcomingToursByArtist SHALL return, for an Artist and a time, each discovered Series (one without an Organizer) of type TOUR that has at least one Event performed by the Artist whose local date is on or after the current date at its Venue at that time, once, with its id and title. It SHALL return an empty list without error when there is none.

#### Scenario: Tour with an upcoming date

- **WHEN** the Artist performs at an Event of a discovered TOUR Series on 2026-12-19 and the time is 2026-11-27
- **THEN** that Series is returned with its title

#### Scenario: Tour already over

- **WHEN** every Event of the Artist's discovered TOUR Series is dated before the current date at its Venue
- **THEN** that Series is not returned

#### Scenario: Standalone show

- **WHEN** the Artist performs at an upcoming Event of a discovered SINGLE Series
- **THEN** that Series is not returned

#### Scenario: Organizer's tour

- **WHEN** the Artist performs at an upcoming Event of a first-party TOUR Series
- **THEN** that Series is not returned
