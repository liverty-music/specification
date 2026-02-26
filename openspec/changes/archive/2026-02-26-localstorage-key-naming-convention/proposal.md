## Why

Frontend localStorage keys use inconsistent naming conventions across three different patterns (`liverty:camelCase`, `liverty:guest:camelCase`, `liverty-music:kebab-case`). This makes keys hard to discover, group, and reason about. Since there are no existing users, now is the time to establish a unified convention before it becomes a breaking change.

Additionally, the key `user-region` stores a prefecture/admin area value but doesn't align with the domain term `admin_area` used in Proto definitions (`Venue.admin_area`) and frontend code (`event.adminArea`).

## What Changes

- **BREAKING**: Rename all localStorage keys to follow a single `[<scope>.]<camelCase>` convention (no namespace prefix)
- Align `user-region` → `userAdminArea` to match the Proto/domain term `admin_area`
- Extract all key constants into a single `storage-keys.ts` module for discoverability
- Update all references across services, components, and E2E tests

### Key Mapping

| Current Key | New Key |
|---|---|
| `liverty:onboardingStep` | `onboardingStep` |
| `liverty:guest:followedArtists` | `guest.followedArtists` |
| `liverty:guest:region` | `guest.adminArea` |
| `liverty-music:user-region` | `user.adminArea` |
| `liverty-music:notifications-enabled` | `user.notificationsEnabled` |
| `liverty-music:notification-prompt-dismissed` | `ui.notificationPromptDismissed` |
| `liverty-music:session-count` | `pwa.sessionCount` |
| `liverty-music:install-prompt-dismissed` | `pwa.installPromptDismissed` |

### Convention

- **No namespace prefix**: localStorage is scoped to the origin, so a prefix is redundant
- **Scope**: `user` (auth-required state), `guest` (anonymous state), `pwa` (PWA-specific), `ui` (UI preferences), no scope for app-level (e.g., `onboardingStep`)
- **Name**: `camelCase`, aligned with Proto/domain terms where applicable
- **Separator**: `.` (dot)

## Capabilities

### New Capabilities
- `localstorage-naming`: Centralized localStorage key registry with consistent naming convention

### Modified Capabilities
_None — this is a refactor of key strings, not a behavioral change._

## Impact

- **Frontend services**: `onboarding-service.ts`, `pwa-install-service.ts`, `local-artist-client.ts`, `settings-page.ts`
- **Frontend components**: `region-setup-sheet.ts`, `area-selector-sheet.ts`, `notification-prompt.ts`
- **E2E tests**: All `pwa-*.spec.ts` files that reference localStorage keys
- **No backend impact**: localStorage is frontend-only
- **No migration needed**: No existing users
