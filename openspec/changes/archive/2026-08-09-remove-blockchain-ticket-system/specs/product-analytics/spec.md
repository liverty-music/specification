## MODIFIED Requirements

### Requirement: The event catalogue records a per-event collection status
The event catalogue SHALL record, for every listed event, a collection status of `active` (currently emitted and consumed) or `dormant` (has a real emitter but is not currently emitting, pending a deferred feature or an external fix). A removed event SHALL NOT remain in the live catalogue table; it SHALL instead be recorded in a dedicated Removed events section together with the reason for removal, so the deletion is documented without reopening the phantom pattern. Dashboards and funnels SHALL be built only on `active` events. The primary conversion funnel SHALL terminate at the last observable step given the current active set — `concert.detail.viewed` — rather than at a `dormant` ticketing event.

#### Scenario: Dashboard is built only on active events
- **WHEN** a dashboard or funnel is defined in PostHog
- **THEN** every step SHALL reference an event catalogued as `active`
- **AND** a step SHALL NOT reference a `dormant` event such as `ticket.email.parsed`

#### Scenario: Deferred ticketing events are dormant, not deleted
- **WHEN** the catalogue lists an implemented-but-inactive event such as `ticket.email.parsed`
- **THEN** the event SHALL be catalogued with status `dormant` and an activation note
- **AND** the event SHALL NOT be counted toward active event volume or listed on any live dashboard

#### Scenario: A removed event is recorded, not silently dropped
- **WHEN** an event is removed from active collection (phantom, redundant, double-counting, firehose, wrong-altitude, or a removed capability such as the blockchain ticket flow)
- **THEN** its row SHALL be removed from the live catalogue table
- **AND** the event SHALL be listed in the Removed events section with the reason for its removal

#### Scenario: Blockchain ticket analytics events are removed
- **WHEN** the blockchain ticket system is removed under the Scenario A pivot
- **THEN** `ticket.mint.completed` and `entry.zk_proof.verified` SHALL be moved from `dormant` to the Removed events section with the reason "blockchain ticket capability removed"
- **AND** neither event SHALL appear in the live catalogue table
