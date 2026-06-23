## 1. PwaInstallService — New Public Getters

- [x] 1.1 Add `browserSupportsPwa` getter: returns `'BeforeInstallPromptEvent' in window`
- [x] 1.2 Add `canShowInstallOption` getter: returns `!this.installed && this.browserSupportsPwa`
- [x] 1.3 Add unit tests for `browserSupportsPwa` (true when `BeforeInstallPromptEvent` in window, false otherwise)
- [x] 1.4 Add unit tests for `canShowInstallOption` (true when not installed + browser supports; false when installed; false when browser unsupported)

## 2. AppShell — Eager Construction

- [x] 2.1 Add `private readonly _pwaInstall = resolve(IPwaInstallService)` to `AppShell` class body
- [x] 2.2 Add a brief comment explaining the field exists to register the `beforeinstallprompt` listener before routing

## 3. PostSignupDialog — Condition & Watcher Refactor

- [x] 3.1 Change `canInstallPwa` getter to use `this.pwaInstall.canShowInstallOption` (drop `canShowFab` + `!isIos`)
- [x] 3.2 Add `@observable public canInstallNatively = false` field
- [x] 3.3 Add private `syncCanInstallNatively()` helper that sets `canInstallNatively = this.pwaInstall.canShowFab && !this.pwaInstall.isIos` (single source for both `binding()` and the watcher)
- [x] 3.4 Seed `canInstallNatively` in `binding()` via `syncCanInstallNatively()` (`@watch` does not fire on initial bind)
- [x] 3.5 Add `@watch((vm: PostSignupDialog) => vm.pwaInstall.canShowFab) canShowFabChanged()` that calls `syncCanInstallNatively()`
- [x] 3.6 Update `isAllDone` getter: replace `!this.canInstallPwa` reference to use `!this.pwaInstall.canShowInstallOption`
- [x] 3.7 Update unit tests: add cases for `canInstallPwa = true` when `canShowInstallOption = true` but `canShowFab = false`
- [x] 3.8 Add unit tests for `canInstallNatively` (starts false; seeded by `binding()`/watcher from `canShowFab && !isIos`)

## 4. PostSignupDialog Template

- [x] 4.1 Update `if.bind="canInstallPwa"` on the install row (condition now driven by `canShowInstallOption`)
- [x] 4.2 Render two mutually-exclusive branches in the install row:
  - Native branch: `if.bind="canInstallNatively"` → existing `busy-on-click.bind="() => onInstallPwa()"` button with `t="postSignup.pwaInstall"`
  - Fallback branch: `if.bind="!canInstallNatively"` → native `<details class="post-signup-install-guide">` disclosure (no ViewModel open/close state)
- [x] 4.3 Inside the fallback `<details>`: `<summary class="post-signup-btn" t="postSignup.pwaInstallGuide">` plus an `<ol class="post-signup-install-steps">` containing three `<li>` items bound to `postSignup.pwaGuideStep1/2/3`

## 5. Styles

- [x] 5.1 Add `.post-signup-install-steps` to `post-signup-dialog.css`: decimal list with left padding, readable line-height (`--leading-relaxed`), consistent font-size with other row body text
- [x] 5.2 Add `.post-signup-install-guide summary` rule: `font-family: var(--font-display)` + `list-style: none` so the `<summary>` reads as a text button without the default disclosure marker

## 6. Translations

- [x] 6.1 Add to `locales/ja/translation.json` under `postSignup`:
  - `"pwaInstallGuide": "追加方法を見る"`
  - `"pwaGuideStep1": "ブラウザ右上のメニュー（⋮）をタップ"`
  - `"pwaGuideStep2": "「ホーム画面に追加」を選択"`
  - `"pwaGuideStep3": "「追加」をタップして完了"`
- [x] 6.2 Add matching keys to `locales/en/translation.json` under `postSignup`:
  - `"pwaInstallGuide": "How to add"`
  - `"pwaGuideStep1": "Tap the menu (⋮) in your browser"`
  - `"pwaGuideStep2": "Select \"Add to Home Screen\""`
  - `"pwaGuideStep3": "Tap \"Add\" to finish"`

## 7. Verification

- [x] 7.1 Run `make check` (lint + unit tests) in the frontend repo — all green
- [x] 7.2 Manually verify on Chrome Android (or DevTools mobile emulation): sign up → celebration → dialog shows install row → tapping "ホーム画面に追加" triggers native prompt
- [x] 7.3 Manually verify fallback path: open in an Incognito window (Chrome does not fire `beforeinstallprompt` there, while `BeforeInstallPromptEvent` still exists → install row shows but native prompt is unavailable), sign in, re-summon the dialog via `localStorage.setItem('liverty:postSignup:shown','pending'); location.reload()`, dismiss the celebration → dialog shows the "追加方法を見る" `<details>` disclosure → toggling expands/collapses the inline steps and is keyboard-operable via the native `<summary>`. (Note: current Chrome DevTools removed the Manifest "Add to homescreen" toggle, so the old block method no longer applies.)
- [x] 7.4 Manually verify iOS: sign up → dialog has no install row → FAB is visible
- [x] 7.5 Open PR targeting `frontend/main`, link this change (#463, Refs #462)
- [x] 7.6 Ship to prod via standard frontend release process (release v1.16.1 → prod AR retag → auto pin-bump cloud-provisioning → ArgoCD Synced/Healthy; web-app + admin-app running v1.16.1, liverty-music.app HTTP 200)
