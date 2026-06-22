## 1. PwaInstallService — New Public Getters

- [ ] 1.1 Add `browserSupportsPwa` getter: returns `'BeforeInstallPromptEvent' in window`
- [ ] 1.2 Add `canShowInstallOption` getter: returns `!this.installed && this.browserSupportsPwa`
- [ ] 1.3 Add unit tests for `browserSupportsPwa` (true when `BeforeInstallPromptEvent` in window, false otherwise)
- [ ] 1.4 Add unit tests for `canShowInstallOption` (true when not installed + browser supports; false when installed; false when browser unsupported)

## 2. AppShell — Eager Construction

- [ ] 2.1 Add `private readonly _pwaInstall = resolve(IPwaInstallService)` to `AppShell` class body
- [ ] 2.2 Add a brief comment explaining the field exists to register the `beforeinstallprompt` listener before routing

## 3. PostSignupDialog — Condition & Watcher Refactor

- [ ] 3.1 Change `canInstallPwa` getter to use `this.pwaInstall.canShowInstallOption` (drop `canShowFab` + `!isIos`)
- [ ] 3.2 Add `@observable public canInstallNatively = false` field
- [ ] 3.3 Add `@watch((vm: PostSignupDialog) => vm.pwaInstall.canShowFab)` → setter that updates `canInstallNatively`
- [ ] 3.4 Initialise `canInstallNatively` in `binding()` from `this.pwaInstall.canShowFab && !this.pwaInstall.isIos`
- [ ] 3.5 Add `public isInstallGuideOpen = false` field
- [ ] 3.6 Add `public onShowInstallGuide(): void` method that sets `isInstallGuideOpen = true`
- [ ] 3.7 Update `isAllDone` getter: replace `!this.canInstallPwa` reference to use `!this.pwaInstall.canShowInstallOption`
- [ ] 3.8 Update unit tests: add cases for `canInstallPwa = true` when `canShowInstallOption = true` but `canShowFab = false`
- [ ] 3.9 Add unit tests for `canInstallNatively` watcher (starts false; becomes true when canShowFab changes to true)
- [ ] 3.10 Add unit tests for `onShowInstallGuide` setting `isInstallGuideOpen = true`

## 4. PostSignupDialog Template

- [ ] 4.1 Update `if.bind="canInstallPwa"` on the install row (condition now driven by `canShowInstallOption`)
- [ ] 4.2 Split install row button into two branches:
  - Native branch: `if.bind="canInstallNatively"` → existing `busy-on-click.bind="() => onInstallPwa()"` button with `t="postSignup.pwaInstall"`
  - Fallback branch: `if.bind="!canInstallNatively && !isInstallGuideOpen"` → button with `click.trigger="onShowInstallGuide()"` and `t="postSignup.pwaInstallGuide"`
- [ ] 4.3 Add inline instruction list: `if.bind="isInstallGuideOpen"` with `<ol class="post-signup-install-steps">` containing three `<li>` items bound to `postSignup.pwaGuideStep1/2/3`

## 5. Styles

- [ ] 5.1 Add `.post-signup-install-steps` to `post-signup-dialog.css`: list-style with left padding, readable line-height, consistent font-size with other row body text

## 6. Translations

- [ ] 6.1 Add to `locales/ja/translation.json` under `postSignup`:
  - `"pwaInstallGuide": "追加方法を見る"`
  - `"pwaGuideStep1": "ブラウザ右上のメニュー（⋮）をタップ"`
  - `"pwaGuideStep2": "「ホーム画面に追加」を選択"`
  - `"pwaGuideStep3": "「追加」をタップして完了"`
- [ ] 6.2 Add matching keys to `locales/en/translation.json` under `postSignup`:
  - `"pwaInstallGuide": "How to add"`
  - `"pwaGuideStep1": "Tap the menu (⋮) in your browser"`
  - `"pwaGuideStep2": "Select \"Add to Home Screen\""`
  - `"pwaGuideStep3": "Tap \"Add\" to finish"`

## 7. Verification

- [ ] 7.1 Run `make check` (lint + unit tests) in the frontend repo — all green
- [ ] 7.2 Manually verify on Chrome Android (or DevTools mobile emulation): sign up → celebration → dialog shows install row → tapping "ホーム画面に追加" triggers native prompt
- [ ] 7.3 Manually verify fallback path: clear site data, block `beforeinstallprompt` (disable in DevTools Application → Manifest → "Add to homescreen"), sign up → dialog shows "追加方法を見る" → tapping expands inline steps
- [ ] 7.4 Manually verify iOS: sign up → dialog has no install row → FAB is visible
- [ ] 7.5 Open PR targeting `frontend/main`, link this change
- [ ] 7.6 Ship to prod via standard frontend release process
