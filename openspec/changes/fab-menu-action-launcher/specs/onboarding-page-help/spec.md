## MODIFIED Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL make page-specific help reachable at all times on the Discovery,
Dashboard, and My Artists pages, for all users regardless of onboarding state, via a
help item in the FAB action launcher (see the `fab-action-launcher` capability). The
page header SHALL NOT host a separate `?` help trigger button; help is contributed as
a launcher item on these pages. Auto-open on first visit (defined by the
"Auto-open on First Page Visit" requirement) opens the same help bottom-sheet
directly and does not depend on the presence of a header trigger.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page
- **THEN** a help item SHALL be present in the FAB action launcher
- **AND** the item SHALL render an icon together with a text label ("ヘルプ")
- **AND** activating it SHALL open that page's help bottom-sheet

#### Scenario: No `?` trigger in the page header

- **WHEN** the Discovery, Dashboard, or My Artists page header is rendered
- **THEN** the header SHALL NOT contain a `?` help trigger button
- **AND** help SHALL be reachable via the FAB action launcher

#### Scenario: Pages without page-specific help contribute no help item

- **WHEN** the user is on a page that has no page-specific help content (e.g. settings)
- **THEN** no help item SHALL be contributed to the launcher for that page
