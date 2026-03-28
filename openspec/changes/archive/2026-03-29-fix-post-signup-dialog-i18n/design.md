## Context

`PostSignupDialog` was built with most user-facing strings correctly using Aurelia 2's `t="..."` attribute binding for i18n. However, two strings were left hardcoded in Japanese:
1. `<h2 class="post-signup-title">✅ アカウント登録完了！</h2>` — the dialog title
2. `aria-label="アカウント登録完了"` on the `<bottom-sheet>` element

When a browser reports `en` as the preferred language, the i18n system activates EN locale, rendering all other dialog text in English — but these two strings remain in Japanese. The fix is purely a template + translation file change; no component logic or service changes are needed.

## Goals / Non-Goals

**Goals:**
- All user-visible strings in `PostSignupDialog` use `t="..."` bindings
- Both JA and EN translation files have a `postSignup.title` key
- `aria-label` is also i18n-bound so screen readers receive the correct locale

**Non-Goals:**
- Fixing i18n issues in other components (separate change if needed)
- Adding new locale support beyond JA and EN
- Changing any TypeScript logic in `post-signup-dialog.ts`

## Decisions

### Use `t` attribute binding for `aria-label`

Aurelia i18n supports binding `aria-label` via `t="[aria-label]postSignup.title"` or by combining with content binding: `t="[aria-label]postSignup.ariaLabel"`. We use a dedicated `postSignup.ariaLabel` key (without the emoji) for the `aria-label`, and `postSignup.title` (with emoji for JA, without for EN) for the `<h2>` text content. This keeps screen reader text clean and culturally appropriate.

**Alternatives considered:**
- Single key for both `<h2>` and `aria-label`: Would force the emoji into the aria-label, which is unconventional for accessibility. Separate keys give clearer control.

### Keep the ✅ emoji in JA translation, omit from EN

The emoji is culturally fitting in the Japanese context. EN translation uses plain text `Account registration complete!` — consistent with other EN UI patterns.

## Risks / Trade-offs

- **Key parity check**: The `frontend-i18n` spec requires both JA and EN files to have matching keys. Adding `postSignup.title` and `postSignup.ariaLabel` to both files satisfies this requirement. [Risk: missing key in one file] → Both files are updated in the same task.

## Migration Plan

No migration needed. This is a pure additive change (new translation keys + template attribute replacement). No existing keys are removed or renamed.
