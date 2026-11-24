## MODIFIED Requirements

### Requirement: Followed artists' concerts in proximity groups

ListFollowed SHALL read the Concerts of the User's followed Artists from the given date, or, when none is given, from the current date at each Concert's Venue (Concert.ListByFollower), and return them as proximity groups relative to the User's home area (Concert.GroupByDateAndProximity), in date order. Concerts of first-party Series that are not publicly visible SHALL NOT be returned.

#### Scenario: Upcoming by default
- **WHEN** no date is given
- **THEN** only Concerts on or after the current date at their own Venue are grouped

#### Scenario: Today differs between venues
- **WHEN** no date is given at 2027-03-15 08:00 in Asia/Tokyo (2027-03-14 23:00 in Europe/London), and followed Artists have Concerts on 2027-03-14 at a Venue in Asia/Tokyo and at a Venue in Europe/London
- **THEN** the Concert at the Venue in Europe/London is grouped and the one at the Venue in Asia/Tokyo is not

#### Scenario: From a past date
- **WHEN** the given date is 7 days ago
- **THEN** Concerts from 7 days ago onward are grouped, with the same grouping and order

#### Scenario: No home area
- **WHEN** the User has no home area
- **THEN** every Concert is in its group's away list

#### Scenario: Follows nothing
- **WHEN** the User follows no Artist
- **THEN** no groups are returned, without error

#### Scenario: Cancelled Organizer concert
- **WHEN** a followed Artist performs in a CANCELLED first-party Series
- **THEN** that Concert is not in any group
