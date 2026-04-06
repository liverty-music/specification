## 1. i18n Translation Keys

- [x] 1.1 Add `postSignup.hypeGuideLabel` key to `frontend/src/locales/ja/translation.json`
- [x] 1.2 Add `postSignup.close` key to `frontend/src/locales/ja/translation.json`
- [x] 1.3 Add `postSignup.hypeGuideLabel` key to `frontend/src/locales/en/translation.json`
- [x] 1.4 Add `postSignup.close` key to `frontend/src/locales/en/translation.json`

## 2. ViewModel

- [x] 2.1 Add `isAllDone` computed getter to `PostSignupDialog`: returns `true` when `!canInstallPwa && notificationManager.permission === 'granted'`

## 3. Template

- [x] 3.1 Add always-visible hype guide hint row (💡 icon, `postSignup.hypeGuideLabel`) to `post-signup-dialog.html`
- [x] 3.2 Update footer button to use `t.bind="isAllDone ? 'postSignup.close' : 'postSignup.defer'"` in `post-signup-dialog.html`

## 4. Tests

- [x] 4.1 Add unit test: hype guide row is always rendered regardless of notification permission and PWA install state
- [x] 4.2 Add unit test: footer button shows "Later" when `canInstallPwa` is true
- [x] 4.3 Add unit test: footer button shows "Later" when `permission !== 'granted'`
- [x] 4.4 Add unit test: footer button shows "Close" when `!canInstallPwa && permission === 'granted'`
