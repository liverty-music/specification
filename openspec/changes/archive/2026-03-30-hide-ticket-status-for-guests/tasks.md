## 1. Frontend — EventDetailSheet ViewModel

- [x] 1.1 Inject `AuthService` into `EventDetailSheet` ViewModel
- [x] 1.2 Add `get isAuthenticated(): boolean` getter delegating to `authService.isAuthenticated`

## 2. Frontend — EventDetailSheet Template

- [x] 2.1 Wrap the Ticket Status section with `if.bind="isAuthenticated"` in `event-detail-sheet.html`

## 3. Validation

- [x] 3.1 Verify that opening the detail sheet as a guest user (onboarding) does not render the Ticket Status section and produces no RPC errors in the console
- [x] 3.2 Verify that opening the detail sheet as an authenticated user still shows the Ticket Status section and SetStatus calls succeed
