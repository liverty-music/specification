## Why

The `PostSignupDialog` component contains hardcoded Japanese strings in its HTML template (`✅ アカウント登録完了！` as the `<h2>` title and `アカウント登録完了` as the `aria-label`) that bypass the `@aurelia/i18n` translation system. When the browser locale is English, all other dialog text correctly renders in English via `t="..."` bindings, but the hardcoded strings remain in Japanese — creating a jarring mix of languages.

## What Changes

- Replace hardcoded `✅ アカウント登録完了！` in `<h2>` with `t="postSignup.title"` binding
- Replace hardcoded `aria-label="アカウント登録完了"` on `<bottom-sheet>` with an i18n-bound value
- Add `postSignup.title` key to both `ja/translation.json` and `en/translation.json`

## Capabilities

### New Capabilities
<!-- None — this is a bug fix within an existing capability -->

### Modified Capabilities
- `post-signup-dialog`: Add i18n requirement that all user-visible strings (including the title and aria-label) MUST use `t` attribute bindings rather than hardcoded text.

## Impact

- `frontend/src/components/post-signup-dialog/post-signup-dialog.html` — template fix
- `frontend/src/locales/ja/translation.json` — add `postSignup.title`
- `frontend/src/locales/en/translation.json` — add `postSignup.title`
- No API or schema changes required
