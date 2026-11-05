## Context

See proposal.md - Why. The current state that shapes the approach:

- **Settings template.** `src/routes/settings/settings-route.html` renders, in order: the guest hero, PREFERENCES (home area, language, push, sound, volume, left-handed), PRIVACY & ANALYTICS (two `settings-consent-row`s and a Privacy Policy `settings-link-row`), ABOUT, NAME ON YOUR TICKETS (an inline `<form>`), ACCOUNT, Sign Out and Delete account. Every card is a `role="list"` of `settings-list-item`s.
- **Actions without confirmation.** `savePersonalDetails()` calls `userStore.updatePersonalDetails()` directly (`settings-route.ts:254-286`); `signOut()` calls `auth.signOut()` directly (`settings-route.ts:656`).
- **The one existing confirmation.** The withdrawal screen holds an inline `<dialog>` opened with `showModal()`, with Cancel focused first (`delete-account-route.html:66-91`, `delete-account-route.ts:145-160`).
- **Bottom sheets** (`src/components/bottom-sheet/`) are non-modal popovers (`showPopover()`), and the shell hides the FAB while any sheet is open (`sheets.anyOpen`).
- **FAB.** `FabMenuService.register(owner, actions)` keeps owner-keyed sets and flattens them into `actions` (`fab-menu-service.ts:79-130`). The shell mounts `<fab-menu>` only when `showNav && fabMenu.actions.length && !sheets.anyOpen` (`app-shell.html:38`), and the nav bar cuts its notch on `fabMenu.actions.length > 0`. Dashboard, Discovery and My Artists register actions; Tickets registers none. `helpAction()` is a shared factory for the per-page help item.
- **Settings gear.** `app-shell.html:14` passes `show-settings.bind="isTabRoute"` to `<page-header>`, which renders `<a href="settings">` (48px, `page-header.css:35-46`). `isTabRoute` is true when the displayed route's config has `nav: true` (`app-shell.ts:338`).
- **Analytics identity.** After sign-in `user-hydration-task.ts:73` calls `identify(user.id)`, so the replay description's 「匿名化された」 is not accurate. Session recording masks every input and every text node (`session-recording.ts:56-58`, `maskAllInputs`, `maskTextSelector: '*'`), which supports the new wording 「入力内容や画面の文字を伏せて」.
- **Support address.** `REPORT_EMAIL_ADDRESS` (`error-boundary-service.ts:8`) is already shown on Settings, in the identity verification failure message.

## Goals / Non-Goals

**Goals:**
- One confirmation component used by Sign Out, the ticket name save and the withdrawal screen.
- The Settings item lives in one place (the shell), not in four tab routes.
- No new RPC, no new stored state.

**Non-Goals:**
- Restyling the settings rows or cards beyond the new order, headings and icons.
- Changing what analytics collects; only the words that describe it change.

## Decisions

### D1. Section order is a template reorder

The sections are reordered in `settings-route.html` per the spec ("Settings sections follow a fixed order"). Two new headings replace PREFERENCES: `settings.sections.notificationsSound` (通知とサウンド / Notifications & sound) and `settings.sections.displayControls` (表示と操作 / Display & controls); `settings.about` becomes 「このアプリについて」 / "About this app". Push stays authenticated-only, so for a guest 通知とサウンド holds Sound Effects and the volume row only. No view-model logic changes. The `verify:build-templates` markers in `scripts/verify-build-templates.lib.ts` are checked against the new template (`npm run build && npm run verify:build-templates`).

*Alternative:* one long list without headings. Rejected: the fan scans by heading, and the spec names the sections.

### D2. Ticket name: a row that opens a bottom sheet

The NAME ON YOUR TICKETS card becomes one `settings-link-row` (icon `ticket`) whose label is the saved full name and whose value is the phone number in domestic form, or 「未設定」 when nothing is saved. Tapping it opens a `<bottom-sheet>` that contains the existing form unchanged (fields, `novalidate`, inline errors, `aria-describedby`). The row reads `savedUser.fullName` and `savedUser.phoneNumber`, the same `User` fields from `UserService.Get` the form reads today, so no new read is needed. Opening the sheet re-seeds the fields from the saved User (`seedPersonalDetails()`), so a cancelled edit never leaks into the next open. After a successful save the sheet closes and the existing 「名義を保存しました。」 snack shows.

*Alternative:* keep the form inline and move it up. Rejected by the user in the plan review: the form breaks the row rhythm of the page.

### D3. A shared `confirm-dialog` component

New `src/components/confirm-dialog/` (presentational, so it gets stories per the frontend story rules):

```ts
// sketch
export class ConfirmDialog {
  @bindable heading = ''
  @bindable body = ''
  @bindable confirmLabel = ''
  @bindable tone: 'default' | 'danger' = 'default'
  /** showModal(); focus Cancel; resolve true on confirm, false on Cancel / Escape / backdrop. */
  ask(): Promise<boolean>
}
```

It is a native `<dialog>` opened with `showModal()`, so it is modal, traps focus, and closes on Escape (the `cancel` event resolves `false`). Cancel receives initial focus (WAI-ARIA APG alert dialog; same as today's withdrawal dialog). The withdrawal screen replaces its inline dialog with this component and keeps its testids, so its behaviour and spec do not change.

Callers `await dialog.ask()` before acting:
- `signOut()`: heading 「サインアウトしますか？」, body 「次に使うときは、パスキーでもう一度ログインします。」, confirm 「サインアウト」.
- `savePersonalDetails()`: validation runs first and an unchanged form still returns early, so the dialog opens only for a real change. Heading 「名義を変更しますか？」; the body shows the new name and phone number (phone in domestic form) on one line, then 「保有中のチケットの券面もこの名義に変わります。」; confirm 「変更する」. Cancel leaves the sheet open with the fan's input.

*Alternatives:* `window.confirm()` — rejected: unstyled, not translatable per locale in the same way, and blocks the thread. A second bottom sheet as the confirmation — rejected: the withdrawal screen and its spec already establish a modal dialog for this pattern.

The confirmation is opened while the name sheet (a non-modal popover) is open. A later `showModal()` enters the top layer above the popover, so the dialog sits over the sheet; the Storybook story and the e2e test check that the dialog is the top-most element at its centre.

### D4. Privacy Policy: one row, one sentence

The consent card's Privacy Policy row is deleted. Below the card a `<p>` holds 「データの扱いは<a>プライバシーポリシー</a>で詳しく説明しています。」; the link calls the existing `openLegal('/legal/privacy')` (root-router navigation, see `SettingsRoute.openLegal`). The About row stays.

### D5. Wording

Locale keys change in `src/locales/{ja,en}/translation.json` (`settings.analytics.*`, `settings.identityVerification.dedupeStrong` / `dedupeWeak`, new section, footnote, contact and dialog keys). Japanese text is fixed by the spec. English text, decided here:

- Section "Help improve the service"; intro "Liverty Music grows with the people who use it. How you use the app is the best clue to what we update next."
- Analytics "Share usage" — "We use it to find where people get lost and where errors happen, and fix them. Your name, email address and phone number are not sent. Turn this off to stop sending usage and error information."
- Session replay "Share screen interaction logs" — "Records taps and scrolls with what you type and the text on screen hidden. We use it to find confusing buttons and steps. Turning this off does not affect any other setting."
- Dedupe: "One account per person, firmly confirmed" / "One account per person, lightly confirmed".

The `settings.analytics.privacyPolicyLink` key is removed.

### D6. Contact row

The About card gains 「お問い合わせ」 / "Contact" (iconless like its neighbours) whose action opens `mailto:${REPORT_EMAIL_ADDRESS}` (the constant Settings already exposes as `supportEmail`). A `mailto:` link needs no new endpoint.

### D7. Distinct icons

Today `info` is shared by the Analytics row and the Privacy Policy row, and `lock` by the Session-replay row and Passkeys. With the policy row gone, two new icons are added to `svg-icon` in the existing stroke style: `chart` for Analytics and `pointer` for Session replay. Passkeys keeps `lock`. The `svg-icon` story set gains them (its screenshot baseline is regenerated per the `visual-baselines` skill).

### D8. Settings as the shell-owned last FAB item

`FabMenuService` gains a trailing slot and a hide flag, both owned outside the route sets:

```ts
// sketch
setTrailing(action: FabAction | null): void   // shell: settingsAction() on tab routes, null elsewhere
hide(owner: object): () => void               // a route hides the launcher; the disposer shows it again
get actions(): FabAction[]                    // [...routeActions, trailing?]; [] while any owner hides it
```

`settingsAction(invoke)` is a factory next to `helpAction()` (`id: 'settings'`, `labelKey: 'fabMenu.settings'`, `icon: 'settings'`, `kind: 'command'`). The app shell sets the trailing item whenever `isTabRoute` changes (on navigation end) and its `invoke` calls `router.load('settings')`; the launcher already closes after a command. Because the slot is appended last, it is always the item farthest from the FAB, and the existing `--i` / `--n` arc bindings place it with no CSS change. My Artists calls `fabMenu.hide(this)` on entering edit mode and disposes it on leaving or detaching, instead of registering an empty set.

The visibility gate in `app-shell.html` and the nav bar notch keep reading `fabMenu.actions.length`, which now includes the trailing item, so Tickets gets the FAB and the notch with no further binding change.

*Alternative:* each tab route registers `settingsAction()` like `helpAction()`. Rejected: four copies, Tickets would need FAB wiring only for this, and a new tab could forget it. The shell already knows `isTabRoute`.

Arc capacity: the dashboard has the most items, four (beam, filter, help, Settings). The 2026-10-19 change verified four items at 320px and 390px (`fab-menu` arc e2e). Discovery reaches three with `polish-fan-web-ui`'s filter item.

### D9. Remove the header gear

`page-header` loses the `show-settings` bindable, the `<a>` and its CSS; its gear story is deleted. `app-shell.html` stops passing it. `nav.settings` stays (the Settings page header label uses it).

### D10. Tests (each ADDED / MODIFIED scenario gets an `@spec` annotation)

- **Unit (Vitest):** `settings-route.spec.ts` — sign-out and save call nothing until confirmed; Cancel calls nothing; unchanged form opens no dialog. `fab-menu-service.spec.ts` — trailing item is last; `hide()` empties `actions` and its disposer restores them.
- **Storybook:** `confirm-dialog` (default, danger, focus on Cancel, Escape resolves false; axe); `svg-icon` new icons.
- **Playwright functional e2e:** section order (signed-in and guest), single Privacy Policy row, contact `mailto:`, name sheet + confirmation, sign-out confirmation, FAB Settings item on all four tabs and last on the dashboard, FAB on Tickets with notch, no FAB in My Artists edit mode, no header gear. Update `e2e/functional/fan-shell-navigation.spec.ts` and `e2e/functional/route-area-banner.spec.ts`, which open Settings through `page-header-settings`, and the fixtures `test/routes/settings-route.fixture.spec.ts` and `test/routes/settings-sign-out.fixture.spec.ts`.

## Risks / Trade-offs

- [Fans who learned the gear look for it in the header] → the product has two users today; the Settings item sits in the same place on every tab.
- [Settings is now two taps away instead of one] → accepted for thumb reach; Settings is opened rarely.
- [The FAB on Tickets carries a single item] → accepted; it keeps one entry point on every tab. A Tickets action can join it later.
- [A modal dialog over a non-modal popover sheet] → covered by the top-layer check in D3's story and e2e.
- [`polish-fan-web-ui` also modifies `global/fab-menu` and `route/my-artists`] → different requirements ("Per-route contextual action registration" and the hype header there; "Global thumb-zone floating launcher" and edit mode here). Whichever change archives second re-reads the main spec first. In code, its Discovery filter item is a route action and composes with the trailing slot.
- [The contact row exposes the support address more widely] → it is already shown in the identity verification failure message on the same page.

## Migration Plan

One frontend PR (one per repository; only frontend changes). No data migration: consent state, handedness and user rows keep their shape. Rollback is a revert. After deploy, check on production with the owner's account: the section order, the FAB Settings item on each tab, the two confirmations (cancel the sign-out; cancel the name change), and that no header gear remains.
