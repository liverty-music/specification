# Tasks

All tasks are in the frontend repository. Run Playwright against a local build (`npm run build` + preview), since the dev environment is stopped.

## 1. Shared confirmation dialog (design D3)

- [ ] 1.1 Add `src/components/confirm-dialog/` (`heading`, `body`, `confirmLabel`, `tone`, `ask(): Promise<boolean>`, native `<dialog>` with `showModal()`, Cancel focused first, Escape and backdrop resolve false) and verify its unit test and stories (default, danger, focus on Cancel, Escape resolves false; axe clean) pass with `npm run test-storybook`
- [ ] 1.2 Replace the withdrawal screen's inline dialog with `confirm-dialog`, keeping its testids, and verify the existing delete-account unit and e2e tests ("Fan confirms", "Fan cancels") pass unchanged

## 2. FAB Settings item and header gear (fab-menu, page-header, bottom-nav-bar, my-artists; design D8, D9)

- [ ] 2.1 Add `settingsAction()`, the trailing slot (`setTrailing`) and `hide(owner)` to `FabMenuService`, and verify `fab-menu-service.spec.ts` covers: the trailing item comes last, `hide()` empties `actions` and its disposer restores them, re-registering a route set keeps the trailing item last
- [ ] 2.2 Set the trailing Settings item from `AppShell` whenever `isTabRoute` changes (its command loads `settings`), add the `fabMenu.settings` key in ja (「設定」) and en ("Settings"), and verify with a unit test that it is set on a tab route and cleared on Settings and on an Event page
- [ ] 2.3 Switch My Artists edit mode from registering an empty set to `fabMenu.hide(this)` (released on Done, on the last artist removed and on detach) and verify the my-artists unit tests for "Entering edit mode reveals remove controls", "Edit offered in the action launcher" and "Edit mode is not persisted across navigation"
- [ ] 2.4 Remove the `show-settings` bindable, the gear link, its CSS and its story from `page-header`, and the binding in `app-shell.html`; verify `npm run lint`, `npm run lint:css` and `npm run test-storybook` pass
- [ ] 2.5 Add Playwright functional e2e with `@spec` annotations for fab-menu "Settings is the last item on the dashboard", "Settings is the only item on Tickets", "Choosing Settings", "No Settings item outside the tabs", "FAB hidden when no actions are contributed", "FAB hidden while the route hides the launcher"; bottom-nav-bar "Tickets shows the FAB", "Route without FAB actions", "Tabs do not move between routes"; and update `e2e/functional/fan-shell-navigation.spec.ts` and `e2e/functional/route-area-banner.spec.ts` to open Settings from the launcher; verify `npx playwright test e2e/functional` passes at 320px and 390px widths

## 3. Settings page order, icons and About (route/settings; design D1, D6, D7)

- [ ] 3.1 Reorder the Settings sections and add the 通知とサウンド and 表示と操作 headings and the 「このアプリについて」 title (ja and en), check the `verify:build-templates` markers with `npm run build && npm run verify:build-templates`, and verify the e2e scenarios "Signed-in fan sees the account first", "Guest sees the hero, then the preferences", "First preferences row is visible on load" and "Authenticated user sees account controls and no guest hero"
- [ ] 3.2 Add the `chart` and `pointer` icons to `svg-icon` with stories, assign them to the Analytics and Session-replay rows, regenerate the `svg-icon` screenshot baseline per the `visual-baselines` skill, and verify the e2e scenario "Consent rows and Passkeys"
- [ ] 3.3 Add the お問い合わせ / Contact row to About (`mailto:` the support address) and verify the e2e scenarios "Legal links" and "Contact support"

## 4. Consent wording and the single Privacy Policy link (route/settings; design D4, D5)

- [ ] 4.1 Delete the consent card's Privacy Policy row, add the footnote with the inline link that calls `openLegal('/legal/privacy')`, remove `settings.analytics.privacyPolicyLink`, and verify the e2e scenario "One Privacy Policy link next to the toggles" (one Privacy Policy row on the page; the footnote link opens `/legal/privacy`)
- [ ] 4.2 Replace the section title, introduction, labels and descriptions in ja (spec text) and en (design D5 text), and verify the e2e scenarios "Analytics toggle is labeled by its purpose", "Session-replay toggle is labeled by its purpose", "No anonymity claim" (no 匿名 / anonym in either locale) and "Both toggles default to on"
- [ ] 4.3 Replace `settings.identityVerification.dedupeStrong` / `dedupeWeak` in ja and en and verify a settings unit test for "Fan verified with My Number Card" (row text, no 重複排除 on the page)

## 5. Confirmed actions on Settings (route/settings; design D2, D3)

- [ ] 5.1 Turn the ticket name card into one row (saved name and phone, or 「未設定」) that opens a bottom sheet holding the existing form, re-seeded on each open and closed after a successful save; verify the unit test and e2e for "No details saved yet"
- [ ] 5.2 Ask `confirm-dialog` before `UserService.Update` in `savePersonalDetails()` (after validation and the unchanged-form check), with the new name and phone in the body, and verify unit tests and e2e for "Fan changes their phone number", "Saving asks first" and "Fan cancels the confirmation" (Update not called; sheet keeps the input), plus a check that the dialog is the top-most element above the sheet
- [ ] 5.3 Ask `confirm-dialog` before `auth.signOut()` and verify unit tests and e2e (updating `test/routes/settings-sign-out.fixture.spec.ts` and `test/routes/settings-route.fixture.spec.ts`) for "Sign out action", "Sign out asks first", "Sign out cancelled", "Sign out apart from account rows" and "Sign out hidden for guests"

## 6. Integration check

- [ ] 6.1 Run `make check` in the frontend and confirm it passes, then open the PR citing `OpenSpec-Change: tidy-fan-settings-page` and the store commit
- [ ] 6.2 After deploy, check production with the owner's account (read-only apart from cancelled dialogs): section order, the FAB Settings item on each of the four tabs, no header gear, the sign-out and name-change dialogs both cancelled without effect
