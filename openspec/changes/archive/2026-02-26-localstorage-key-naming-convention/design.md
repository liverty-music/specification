## Context

The frontend stores 8 localStorage keys using 3 inconsistent patterns. All keys need to be renamed to follow a unified convention. There are no existing users, so no migration logic is needed.

## Goals / Non-Goals

**Goals:**
- Establish a single, consistent localStorage key naming convention
- Align domain terms with Proto definitions (`admin_area` instead of `region`)
- Centralize all key constants into one module for discoverability
- Update all E2E tests to use the new keys

**Non-Goals:**
- Adding a localStorage abstraction layer or wrapper service
- Changing stored values or serialization format
- Backward-compatible migration logic (no users exist)

## Decisions

### 1. Convention: `[<scope>.]<camelCase>` (no namespace prefix)

```
onboardingStep                  # app-level (no scope)
user.adminArea                  # authenticated user state
guest.followedArtists           # anonymous/guest state
pwa.sessionCount                # PWA-specific
ui.notificationPromptDismissed  # UI preferences
```

**Rationale**: localStorage is scoped to the origin, so a namespace prefix is redundant. Dot-separated scopes are readable, sortable in DevTools, and group related keys logically.

### 2. Single `storage-keys.ts` module

All key constants are defined in `src/constants/storage-keys.ts` and exported as a flat object:

```typescript
export const StorageKeys = {
  onboardingStep: 'onboardingStep',
  userAdminArea: 'user.adminArea',
  guestFollowedArtists: 'guest.followedArtists',
  guestAdminArea: 'guest.adminArea',
  userNotificationsEnabled: 'user.notificationsEnabled',
  uiNotificationPromptDismissed: 'ui.notificationPromptDismissed',
  pwaSessionCount: 'pwa.sessionCount',
  pwaInstallPromptDismissed: 'pwa.installPromptDismissed',
} as const
```

**Rationale**: A single registry prevents duplicate/divergent key definitions. Each consuming module imports from this one source.

### 3. Domain term alignment: `region` → `adminArea`

The Proto schema uses `admin_area` (from Google AIP `postal_address.admin_area`). The frontend `dashboard-service.ts` already uses `adminArea` internally. Renaming the localStorage key aligns the persistence layer with the domain model.

## Risks / Trade-offs

- **DevTools familiarity**: Developers accustomed to the old keys will need to update their mental model. The centralized `storage-keys.ts` module mitigates this.
- **E2E test strings**: All E2E tests that hardcode localStorage key strings must be updated. Using `StorageKeys` import in tests would be ideal but may not work with `page.evaluate()` contexts — string literals are acceptable in E2E tests.
