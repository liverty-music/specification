# components/adapter/organizer/api/rpc/ticket-sale Specification

## Purpose
The organizer-facing ticket sale service boundary: how a member's sign-in is turned into their own Organizer before a sale is configured or read.

## Requirements

### Requirement: Every call acts for the caller's own active Organizer

Create, ListByEvent, SetWindow and SetVerificationRequirement SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. When the caller has no Organization, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs: PermissionDenied when no Organizer is linked to the Organization or the Organizer is provisioning, and FailedPrecondition when it is deactivated. Only then SHALL the boundary run, for the resolved Organizer, TicketSaleUseCase.Create for Create, ListOwnByEvent for ListByEvent, SetWindow for SetWindow and SetVerificationRequirement for SetVerificationRequirement; errors from the usecase SHALL be returned unchanged. That the Series, event or sale belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Member configures a sale

- **WHEN** a member of an active Organizer calls Create for a FirstCome or Lottery sale on its published events
- **THEN** the sale is created and returned naming its events

#### Scenario: Member sees how many sold

- **WHEN** a member calls ListByEvent for their event
- **THEN** TicketSaleUseCase.ListOwnByEvent runs for their Organizer and the event's sales are returned with the entry stats of each TicketStock

#### Scenario: Member moves a window

- **WHEN** a member calls SetWindow for a sale on their Series
- **THEN** TicketSaleUseCase.SetWindow runs for their Organizer and the updated sale is returned

#### Scenario: Organization with no Organizer

- **WHEN** no Organizer is linked to the caller's Organization
- **THEN** the call fails with PermissionDenied and nothing is created

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition

### Requirement: Calls name their events and values

Each call SHALL fail with InvalidArgument, before any usecase runs, when a value it needs is missing or malformed:
- Create, when no Series, name, method, start time, end time or event is given;
- ListByEvent, when no event is given;
- SetWindow, when no sale, start time or end time is given;
- SetVerificationRequirement, when no sale is given. A request that gives no requirement sets None.

#### Scenario: Sale without events

- **WHEN** Create is called with no event
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Create without an end time

- **WHEN** Create is called without an end time
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: ListByEvent without an event

- **WHEN** ListByEvent is called without an event
- **THEN** it fails with InvalidArgument

#### Scenario: SetWindow without an end time

- **WHEN** SetWindow is called without an end time
- **THEN** it fails with InvalidArgument and nothing changes

### Requirement: A window is local date-times in one time zone

Create and SetWindow SHALL take the sale's start time and end time each as a local date-time, a calendar date and a time of day, together with one IANA time zone in which both are read; the sale is created, or its window is set, in that time zone. Each call SHALL fail with InvalidArgument, before any usecase runs, when the time zone is missing or is not an IANA time zone name, when a start or end time is given with a UTC offset instead of the time zone, or when the start time and the end time name different time zones, or when a start or end time has a month, day, hour or minute out of range, a second or a fraction of a second, or a day that does not exist in its month (30 February). A call SHALL also fail with InvalidArgument, before any usecase runs, when a local date-time does not exist in the time zone, because the clocks skip it, since no instant can be computed for it. Every sale the boundary returns SHALL carry its start time and end time as local date-times with its time zone.

#### Scenario: Sale for a show abroad

- **WHEN** a member calls Create for a Lottery sale from 2026-11-01 12:00 to 2026-11-07 23:59 in the time zone Asia/Taipei
- **THEN** the sale is created in Asia/Taipei and returned with the start 2026-11-01 12:00 and the end 2026-11-07 23:59, each with the time zone Asia/Taipei

#### Scenario: Time with seconds or a day that does not exist
- **WHEN** Create is called with a start time of 2027-02-30 12:00, or with an end time of 2027-03-01 12:00:30
- **THEN** it fails with InvalidArgument before any usecase runs and nothing is stored

#### Scenario: Window without a time zone

- **WHEN** SetWindow is called with a start and an end time and no time zone
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Offset instead of a time zone

- **WHEN** Create is called with a start time given as 2026-11-01 12:00 at UTC+09:00
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Start and end in different time zones

- **WHEN** Create is called with a start time in Asia/Tokyo and an end time in Asia/Seoul
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Time skipped by the clock change

- **WHEN** SetWindow is called with a start time of 2027-03-14 02:30 in the time zone America/New_York, a time the clocks skip that night
- **THEN** it fails with InvalidArgument before any usecase runs and nothing changes
