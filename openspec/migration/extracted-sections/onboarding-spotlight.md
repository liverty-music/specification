<!-- Extracted 2026-09-21 from openspec/specs/onboarding-spotlight/spec.md lines 234-309.
     Non-product sections removed so the spec has only Purpose and Requirements.
     Sections: Test Cases
     Routed in Phase 1 manifest (OUT:design-doc / OUT:delete). -->

## Test Cases

### Unit Tests (Vitest — coach-mark.spec.ts)

#### TC-SP-01: Target element receives anchor-name when highlighted

- **Given** a coach mark component is created
- **When** `activateSpotlight(selector, message, onTap)` is called with a valid target selector
- **Then** the target element's `anchorName` style SHALL be set to `--coach-target`

#### TC-SP-02: Popover opens only once (continuous persistence)

- **Given** the coach mark is not yet visible
- **When** `activateSpotlight()` is called for the first time
- **Then** `showPopover()` SHALL be called once on the overlay element
- **When** `activateSpotlight()` is called again with a different target
- **Then** `showPopover()` SHALL NOT be called again

#### TC-SP-03: Target change does not close popover

- **Given** the coach mark is active with target A
- **When** `activateSpotlight()` is called with target B
- **Then** `hidePopover()` SHALL NOT be called
- **And** target A's `anchorName` SHALL be cleared
- **And** target B's `anchorName` SHALL be set to `--coach-target`

#### TC-SP-04: Deactivate cleans up all state

- **Given** the coach mark is active
- **When** `deactivateSpotlight()` is called
- **Then** `hidePopover()` SHALL be called on the overlay element
- **And** the current target's `anchorName` SHALL be cleared
- **And** scroll lock on `<au-viewport>` SHALL be released (`overflow` reset)

#### TC-SP-05: Arrow direction resolves to 'up' or 'down'

- **Given** the coach mark is active
- **When** the tooltip position is `block-end` (below target)
- **Then** `arrowDirection` SHALL be `'up'`
- **When** the tooltip position is `block-start` (above target)
- **Then** `arrowDirection` SHALL be `'down'`

#### TC-SP-06: Blocker click invokes onTap callback

- **Given** the coach mark is active with an `onTap` callback
- **When** the user clicks a `.click-blocker` element
- **Then** the `onTap` callback SHALL be invoked

#### TC-SP-07: spotlightRadius defaults to '12px'

- **Given** the coach mark is activated without specifying spotlightRadius
- **Then** the `--spotlight-radius` CSS custom property SHALL default to `'12px'`

#### TC-SP-08: Target retry with exponential backoff

- **Given** the target element does not exist in the DOM
- **When** `activateSpotlight()` is called
- **Then** the system SHALL retry finding the target (using fake timers to advance)
- **And** the system SHALL find and highlight the target once it appears

#### TC-SP-09: Target interceptor intercepts clicks

- **Given** the coach mark is active with a target
- **When** the user clicks the `.target-interceptor` overlay
- **Then** `preventDefault()` and `stopPropagation()` SHALL be called on the event
- **And** the `onTap` callback SHALL be invoked

### E2E Tests (Playwright — manual verification)

#### TC-SP-E2E-01: Full onboarding spotlight continuity

- Verify spotlight opens at Step 1 and persists through Step 5 without blinking
- Verify View Transition slide animation between targets
- Verify tooltip text updates at each step
- Verify cleanup at Step 6: no anchor-name, no scroll lock, popover hidden
