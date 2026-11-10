## ADDED Requirements

### Requirement: Tab switches cross-fade

Switching between the routes of the bottom navigation bar's tabs SHALL animate, so the fan sees one screen give way to the next instead of a cut. The outgoing route SHALL fade out while the incoming route fades in, and the navigation bar and page header SHALL stay in place without fading. Under reduced motion every such switch, and every other animated screen change, SHALL be instant. Route changes that do not start from a tab SHALL change without an animation.

#### Scenario: Tab switch

- **WHEN** the fan taps the My Artists tab while Home is shown
- **THEN** Home fades out and My Artists fades in within 250-350 ms
- **AND** the navigation bar and the page header do not fade

#### Scenario: Reduced motion preference

- **WHEN** the fan has asked the system for reduced motion and taps another tab
- **THEN** the new route is shown at once, with no fade

#### Scenario: Route change from inside a page

- **WHEN** the fan opens a concert's event page from the timetable
- **THEN** the event page is shown without a page transition

## REMOVED Requirements

### Requirement: Page Transition Animations

**Reason**: It required every route change to fade and slide, forward and backward, but no route transition was ever built: the shell renders a plain router viewport, and the only screen animations are the in-place edits in Discovery and My Artists. A requirement no code meets is not a guarantee.
**Migration**: Replaced by "Tab switches cross-fade", which covers the switches this change animates. Other route changes stay instant, as they are today.
