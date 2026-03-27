## ADDED Requirements

### Requirement: Dialog reliably opens when active is true at creation time
The PostSignupDialog SHALL reliably open when `active` is bound to `true` at component creation time, not only when `active` transitions from `false` to `true` after the component is attached.

#### Scenario: Dashboard sets showPostSignupDialog in loading() before attach
- **WHEN** `DashboardRoute.loading()` sets `showPostSignupDialog = true`
- **AND** `PostSignupDialog` receives `active = true` during its `binding` phase
- **THEN** `activeChanged()` SHALL set `isOpen = true`
- **AND** the inner `<bottom-sheet>` SHALL open successfully (via the `attached()` fallback in BottomSheet)
- **AND** the dialog SHALL be visible to the user with its full content
