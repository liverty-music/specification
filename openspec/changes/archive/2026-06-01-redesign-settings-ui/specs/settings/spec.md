## ADDED Requirements

### Requirement: Toggle Control Layout Integrity

The system SHALL render each Settings toggle switch at a fixed control size whose visual thumb remains fully contained within the toggle track and within the enclosing card, independent of the length of any adjacent label or description in the same row. The toggle track SHALL NOT shrink below its declared size when competing for horizontal space with sibling content.

#### Scenario: Toggle paired with a long multi-line description

- **WHEN** a toggle row is rendered with a description long enough to wrap onto multiple lines
- **THEN** the toggle track SHALL retain its declared control width (it SHALL NOT collapse)
- **AND** the toggle thumb SHALL remain fully inside the track in both the ON and OFF positions
- **AND** no part of the thumb or track SHALL overflow the right edge of the enclosing card

#### Scenario: Toggle vertical alignment against multi-line content

- **WHEN** a toggle row's text column spans multiple lines
- **THEN** the toggle control SHALL align to the first line of the label it controls rather than floating to the vertical centre of the whole text block

---

### Requirement: Expandable Toggle Description

The system SHALL allow a toggle row's descriptive text to be collapsed by default and expanded on demand, without compromising the accessibility semantics of the switch. The expand/collapse control and the switch SHALL be distinct, sibling interactive elements — the switch SHALL NOT contain another interactive control.

#### Scenario: Collapsed description with expand affordance

- **WHEN** a toggle row has a collapsible description and is in the collapsed state
- **THEN** the description SHALL NOT be rendered (the label and the expand affordance serve as the summary)
- **AND** an expand affordance (e.g. a rotating chevron) SHALL be shown next to the label to indicate more content is available

#### Scenario: Expanding and collapsing the description

- **WHEN** the user activates the description's disclosure control
- **THEN** the full description SHALL be revealed and the disclosure control's `aria-expanded` state SHALL reflect "true"
- **AND** activating it again SHALL collapse the description and set `aria-expanded` to "false"
- **AND** toggling the disclosure SHALL NOT change the switch's on/off value

#### Scenario: Switch remains operable and accessibly separate

- **WHEN** a toggle row presents both a disclosure control and a switch
- **THEN** the switch SHALL expose `role="switch"` with `aria-checked` reflecting its value
- **AND** the switch SHALL be an interactive element that is a sibling of (not a descendant of) the disclosure control
- **AND** the switch's activation target SHALL be at least 24px on both axes (WCAG 2.5.8 AA), with the adjacent disclosure control providing a larger neighbouring target — the row no longer adds block-axis padding to the switch, so the track sits pixel-aligned with the other rows' trailing controls (see design decision D0: card-grid + row-subgrid)

#### Scenario: No expand affordance when nothing to expand

- **WHEN** a toggle row has no description, or a description that fits within the collapsed length
- **THEN** no expand affordance SHALL be shown

---

### Requirement: Privacy & Analytics Consent Toggle Labeling

The Settings page SHALL present the analytics consent toggles using labels and descriptions that name the consent *purpose* (what the data is used for), not the data's processing *geography*. Each consent toggle on the Settings page SHALL remain a persistent, user-controlled opt-out for the corresponding consent purpose. The Settings page SHALL NOT present a per-region ("domestic" vs "overseas") processing toggle, and SHALL NOT remove a consent purpose's Settings opt-out while that purpose can be granted at signup.

#### Scenario: Product-analytics toggle is purpose-labeled

- **WHEN** the Privacy & Analytics section is rendered
- **THEN** the product-analytics toggle SHALL be bound to the product-analytics consent purpose
- **AND** its label and description SHALL describe improving the product experience from anonymous usage data
- **AND** its description SHALL state that no personally identifying information is collected

#### Scenario: Marketing-measurement toggle is purpose-labeled (not geography)

- **WHEN** the Privacy & Analytics section is rendered
- **THEN** the second toggle SHALL be bound to the `marketingMeasurement` consent purpose
- **AND** its label and description SHALL describe ad-effectiveness measurement, not "overseas" or "cross-border" data processing
- **AND** turning it off SHALL be stated to have no effect on other features

#### Scenario: Settings opt-out persists for a purpose granted at signup

- **WHEN** a user granted a consent purpose at the signup consent screen
- **THEN** the Settings page SHALL render a corresponding toggle that lets the user withdraw that consent
- **AND** the toggle SHALL reflect the persisted consent state on load

---

### Requirement: Platform-Conditional Sound Effects Hint

The Settings page SHALL only show the iOS-specific sound-effects behavior hint on iOS devices. On non-iOS platforms the system SHALL NOT display a hint that references iOS-only behavior.

#### Scenario: iOS device shows the iOS hint

- **WHEN** the Settings page is rendered on an iOS device
- **THEN** the sound-effects row SHALL display the iOS-specific hint about the device's silent/manner mode

#### Scenario: Non-iOS device does not show the iOS hint

- **WHEN** the Settings page is rendered on a non-iOS platform (Android, desktop)
- **THEN** the sound-effects row SHALL NOT display the iOS-specific hint

## MODIFIED Requirements

### Requirement: Guest-Adaptive Account Section

The system SHALL adapt the Settings page to authentication state. For guests, the system SHALL present the sign-in / sign-up call to action as a visually emphasized hero placed at the TOP of the Settings page (before the preferences content), and SHALL hide account-bound controls (email address, email verification status, resend-verification, sign-out). For authenticated users, the system SHALL NOT render the guest hero, and the bottom ACCOUNT section SHALL present the existing account controls.

#### Scenario: Guest sees a prominent sign-in hero at the top

- **WHEN** an unauthenticated user views the Settings page
- **THEN** the system SHALL render a guest call-to-action hero at the top of the page, above the preferences content
- **AND** the hero SHALL be visually distinct from the standard list cards (e.g. brand-tinted background and a filled primary action)
- **AND** the hero SHALL offer a primary "ログイン" action and a secondary "新規登録" action that initiate the OIDC sign-in / sign-up flow
- **AND** the email address row, email-verification badge, and resend-verification button SHALL NOT be rendered

#### Scenario: Authenticated user sees account controls and no guest hero

- **WHEN** an authenticated user views the Settings page
- **THEN** the system SHALL NOT render the guest hero
- **AND** the bottom ACCOUNT section SHALL render the email address, the verification badge, the resend-verification button (when unverified), and the Sign Out control
