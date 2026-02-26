## 1. Create centralized key registry

- [x] 1.1 Create `src/constants/storage-keys.ts` with `StorageKeys` object containing all 8 key constants

## 2. Update services

- [x] 2.1 Update `src/services/onboarding-service.ts`: import `StorageKeys.onboardingStep`, remove local `STORAGE_KEY`
- [x] 2.2 Update `src/services/pwa-install-service.ts`: import `StorageKeys.pwaSessionCount` and `StorageKeys.pwaInstallPromptDismissed`, remove local constants
- [x] 2.3 Update `src/services/local-artist-client.ts`: import `StorageKeys.guestFollowedArtists` and `StorageKeys.guestAdminArea`, remove local constants, rename `REGION_KEY` references to `adminArea`

## 3. Update components

- [x] 3.1 Update `src/components/region-setup-sheet/region-setup-sheet.ts`: import `StorageKeys.userAdminArea`, remove local `REGION_STORAGE_KEY` export
- [x] 3.2 Update `src/components/area-selector-sheet/area-selector-sheet.ts`: import from `storage-keys.ts` instead of `region-setup-sheet.ts`
- [x] 3.3 Update `src/components/notification-prompt/notification-prompt.ts`: import `StorageKeys.uiNotificationPromptDismissed`, remove local constant
- [x] 3.4 Update `src/routes/settings/settings-page.ts`: import `StorageKeys.userNotificationsEnabled`, remove local constant

## 4. Update E2E tests

- [x] 4.1 Update `e2e/pwa-install-prompt.spec.ts`: update all localStorage key strings in `ONBOARDING_SETUP` and `addInitScript` calls
- [x] 4.2 Update `e2e/pwa-settings.spec.ts` if it references any localStorage keys (none found)
- [x] 4.3 Update `e2e/pwa-offline-cache.spec.ts` if it references any localStorage keys (none found)

## 5. Verify

- [x] 5.1 Run `tsc --noEmit` to verify no type errors
- [x] 5.2 Run unit tests
- [x] 5.3 Run Playwright E2E tests for PWA specs (key strings updated; verified via CI)
