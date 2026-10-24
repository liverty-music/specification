## MODIFIED Requirements

### Requirement: Draft becomes live

Publish SHALL take a Series and, optionally, some of its Events; when no Event is named it SHALL publish every DRAFT Event of the Series. It SHALL publish them with Series.PublishEvents. A slot held by another Organizer or a slot held by a CANCELLED Event SHALL fail the publish with FailedPrecondition and nothing is published; there is no override. A slot where an admin deleted a Concert SHALL NOT fail the publish. A named Event that is not DRAFT, or a Series with no DRAFT Event when none is named, SHALL fail with FailedPrecondition.

#### Scenario: Claims a discovered event
- **WHEN** a DRAFT Event's slot holds a discovered Event with fan TicketJourneys
- **THEN** that Event joins the Series as PUBLISHED with its id and TicketJourneys kept

#### Scenario: Suppressed slot
- **WHEN** a DRAFT Event's slot was suppressed by an admin's delete and no Event is at that slot
- **THEN** Publish succeeds and the Event becomes PUBLISHED

#### Scenario: Already published
- **WHEN** the owner publishes a Series that has no DRAFT Event
- **THEN** Publish fails with FailedPrecondition

#### Scenario: Additional date on a published tour
- **WHEN** the owner publishes the one DRAFT Event of a Series whose other Events are PUBLISHED
- **THEN** that Event becomes PUBLISHED and the other Events are unchanged

#### Scenario: Only the named date
- **WHEN** a Series has two DRAFT Events and the owner names one of them
- **THEN** only the named Event is published and the other stays DRAFT
