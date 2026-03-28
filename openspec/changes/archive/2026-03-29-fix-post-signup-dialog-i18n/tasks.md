## 1. Translation Keys

- [x] 1.1 Add `postSignup.title` key to `frontend/src/locales/ja/translation.json` with value `✅ アカウント登録完了！`
- [x] 1.2 Add `postSignup.ariaLabel` key to `frontend/src/locales/ja/translation.json` with value `アカウント登録完了`
- [x] 1.3 Add `postSignup.title` key to `frontend/src/locales/en/translation.json` with value `Account registration complete!`
- [x] 1.4 Add `postSignup.ariaLabel` key to `frontend/src/locales/en/translation.json` with value `Account registration complete`

## 2. Template Fix

- [x] 2.1 Replace `<h2 class="post-signup-title">✅ アカウント登録完了！</h2>` with `<h2 class="post-signup-title" t="postSignup.title"></h2>` in `post-signup-dialog.html`
- [x] 2.2 Replace `aria-label="アカウント登録完了"` on `<bottom-sheet>` with `t="[aria-label]postSignup.ariaLabel"` in `post-signup-dialog.html`

## 3. Verification

- [x] 3.1 Run `make lint` in `frontend/` and confirm no errors
- [x] 3.2 Run `make test` in `frontend/` and confirm no regressions
