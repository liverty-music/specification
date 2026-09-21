<!-- spec: ticket-journey | target: components/infrastructure/fan/web/global/event-detail-sheet | flags: CLASSNAME | new_name: Ticket Status UI two-phase layout -->

### Requirement: Ticket Status UI two-phase layout

The Ticket Status control in the event detail sheet SHALL present the journey statuses in two phases instead of a flat row: a **process phase** (`TRACKING ▸ APPLIED`) and an **outcome phase**. The outcome phase SHALL stack its routes vertically with the success route (`UNPAID → PAID`, grouped under a "当選" heading) above the failure route (`LOST`).

#### Scenario: Process phase shows the pre-result sequence

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the process phase SHALL render `TRACKING` and `APPLIED` as a horizontal segmented sequence in that order

#### Scenario: Outcome phase stacks success above failure

- **WHEN** the outcome phase is rendered
- **THEN** the success route (`UNPAID` then `PAID`) SHALL appear above the failure route (`LOST`)
- **AND** `UNPAID` and `PAID` SHALL be grouped under a single "当選" heading
