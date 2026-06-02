## ADDED Requirements

### Requirement: Language Selector Single-Select Semantics
The language selection UI SHALL be exposed to assistive technology as a single-select control so screen-reader users can perceive which language is active and that exactly one may be chosen. A visual-only `data-selected` highlight with an `aria-hidden` check icon SHALL NOT be the sole indicator of selection.

#### Scenario: Language options form a radiogroup
- **WHEN** the language selection UI is displayed
- **THEN** the option container SHALL expose `role="radiogroup"` (or use native `<input type="radio">`) with an accessible group name
- **AND** each language option SHALL expose `role="radio"` (or be a native radio) with `aria-checked` reflecting whether it is the active language
- **AND** the currently active language option SHALL have `aria-checked="true"` and all others `aria-checked="false"`

#### Scenario: Selected language is announced
- **WHEN** a screen-reader user navigates the language options
- **THEN** the active option SHALL be announced as the checked/selected radio
- **AND** selection state SHALL NOT depend on a CSS `data-selected` attribute or an `aria-hidden` check icon alone

---

### Requirement: Home Area Selected-State Indicator
The home-area selector SHALL indicate the currently selected prefecture/city reactively, consistent with the language selector's selected-state treatment.

#### Scenario: Current home area is highlighted
- **WHEN** the home-area selector is open and the user has a current home area
- **THEN** the option matching `userStore.currentHome` SHALL carry a selected-state indicator (`aria-checked`/`data-selected`) bound off the observable `userStore.currentHome`
- **AND** the indicator SHALL update reactively if the current home area changes

---

### Requirement: Settings Async Status Live Region
Asynchronous status changes on the Settings page SHALL be announced to assistive technology via a polite live region rather than updating silently.

#### Scenario: Resend-verification status is announced
- **WHEN** the resend-verification button transitions between its states (idle → "Sending…" → "Sent")
- **THEN** the status change SHALL be conveyed through an `aria-live="polite"` region
- **AND** the email verification badge transition (Verified ↔ Not-verified) SHALL likewise be announced politely

---

### Requirement: Toggle Hint Association And Disabled Push Row
Descriptive hint text for a toggle row SHALL be programmatically associated with its control, and a control that is unavailable due to missing configuration SHALL remain discoverable by assistive technology.

#### Scenario: Toggle hint associated via aria-describedby
- **WHEN** a toggle row (`role="switch"`) has accompanying hint/description text
- **THEN** the switch SHALL reference that text via `aria-describedby`

#### Scenario: VAPID-unavailable push row stays discoverable
- **WHEN** push notifications are unavailable because the VAPID public key is missing
- **THEN** the push row SHALL use `aria-disabled="true"` plus an explanation rather than the native `disabled` attribute (which removes the control from assistive-technology discovery)

---

### Requirement: Settings Group List Semantics
Each Settings card SHALL expose list semantics so assistive technology announces a bounded list of items rather than a flat run of buttons interspersed with separator noise.

#### Scenario: Cards expose list semantics
- **WHEN** a Settings card containing multiple rows is rendered
- **THEN** the card SHALL use `role="list"` (or `<ul>`) with each row as a `role="listitem"` (or `<li>`)
- **AND** decorative `<hr>` separators between rows SHALL be removed (visual separation handled by CSS)

---

### Requirement: Email And Verification Badge Association
The account email and its verification badge SHALL be programmatically associated, and verification status SHALL be conveyed by more than color alone.

#### Scenario: Badge associated with email and not color-only
- **WHEN** the account section renders the email address and the Verified / Not-verified badge
- **THEN** the badge SHALL be programmatically associated with the email (e.g., via `aria-describedby` or an accessible-name relationship)
- **AND** the badge SHALL convey status with a non-color cue (text and/or icon) in addition to color

---

### Requirement: Consent Toggle Observable Binding
The Settings consent toggles SHALL bind directly to the observable consent state owned by `ConsentService`, with no component-local mirror of that state.

#### Scenario: Consent toggles reflect service state without a mirror
- **WHEN** the Settings page renders the analytics / marketing-measurement consent toggles
- **THEN** the `aria-checked` and `data-on` bindings SHALL derive from `ConsentService`'s `@observable` state directly
- **AND** the component SHALL NOT maintain `analyticsConsent` / `marketingConsent` mirror fields or write-back handlers

#### Scenario: External consent change updates the toggles
- **WHEN** consent state changes outside the Settings toggle handlers (e.g., via the onboarding consent screen earlier in the session)
- **THEN** the Settings toggles SHALL reflect the new state on next render without manual re-sync

---

### Requirement: Language Selection Sheet Dismiss And Error Surfacing
The language selection sheet SHALL close after a selection is applied (or is a no-op), and a non-`ConnectError` failure SHALL be surfaced rather than leaving the row silently stale.

#### Scenario: Sheet closes after successful change
- **WHEN** a user selects a language different from the current one and the change is applied successfully
- **THEN** the selection sheet SHALL close after the change is applied
- **AND** the Language row SHALL reflect the new language

#### Scenario: Re-selecting the current language closes without an RPC
- **WHEN** a user selects the language already in effect
- **THEN** the sheet SHALL close and no RPC SHALL be issued

#### Scenario: Non-ConnectError failure is surfaced
- **WHEN** applying a language change raises a non-`ConnectError` (a programmer error reaching the handler)
- **THEN** the error SHALL propagate to the global error boundary
- **AND** the UI SHALL NOT present a silently dismissed sheet with the row still showing the old language as if the change succeeded
