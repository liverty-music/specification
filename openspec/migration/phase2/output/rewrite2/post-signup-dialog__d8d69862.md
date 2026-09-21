<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/post-signup-dialog | flags: CLASSNAME | new_name: PWA Install Row Shows Fallback Instructions When Native Prompt Unavailable -->

### Requirement: PWA Install Row Shows Fallback Instructions When Native Prompt Unavailable

When the browser supports PWA install but the native prompt has not been captured, the post-signup dialog SHALL show a manual install guide rather than hiding the row.

#### Scenario: Install row shows "How to add" disclosure when deferredPrompt is absent

- **WHEN** the post-signup dialog is displayed
- **AND** the browser supports PWA install
- **AND** the native install prompt has not yet been captured
- **THEN** the install row SHALL display a "How to add" disclosure control (a native `<details>`/`<summary>` rendered as a button) instead of the native install button
- **AND** the disclosure SHALL be collapsed by default (the instruction steps hidden)

#### Scenario: Toggling "How to add" reveals inline instructions

- **WHEN** the user activates the "How to add" disclosure (click, or keyboard via the native `<summary>`)
- **THEN** the install row SHALL expand to show numbered steps for browser-menu-based installation:
  1. Open the browser menu (⋮)
  2. Select "Add to Home Screen"
  3. Tap "Add" to finish
- **AND** the "How to add" summary SHALL remain visible above the expanded steps and stay toggleable (the native disclosure can be collapsed again)

#### Scenario: Install row reactively upgrades to native button on prompt arrival

- **WHEN** the post-signup dialog is open
- **AND** the browser fires `beforeinstallprompt` (native prompt arrives after dialog opened)
- **THEN** the native install prompt becomes available
- **AND** the install row SHALL update reactively to show the native install button
- **AND** the "How to add" disclosure SHALL be replaced by the native install button
