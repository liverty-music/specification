## Context

The `users.preferred_language` column exists in the DB with `DEFAULT 'en'` and the Go `entity.User.PreferredLanguage` field is populated by the repository — but the proto layer never exposes it. As a result, the only effective store for the user's language preference is browser `localStorage` written by `changeLocale()` (`frontend/src/util/change-locale.ts`).

Symptoms observed in production: after a user switches the language in Settings, a hard reload occasionally falls back to EN. The most likely failure surfaces are localStorage volatility (Safari ITP cap, private browsing, cross-device divergence) and the absence of a recovery path — there is no server-side fallback when `localStorage` is missing or stale. Even without a confirmed root cause, the only durable fix is to make the backend the source of truth once an account exists.

Pre-signup, the user is anonymous — the only place to remember a language choice is the browser. The existing i18next-browser-languagedetector chain (`['querystring', 'localStorage', 'navigator']`) is already correct for anonymous users, but `caches: []` means navigator-detected values are NOT persisted, so each reload re-detects from `navigator.language` instead of remembering a stable choice.

## Goals / Non-Goals

**Goals:**
- Make `users.preferred_language` the single source of truth for authenticated users.
- Capture the user's pre-signup effective locale at Create time and persist it.
- Persist navigator-detected locale to `localStorage` on first visit so anonymous reload behavior is stable.
- After signup, remove `localStorage['language']` and never read it again while signed in.
- Provide a backfill path for existing rows so they aren't permanently stuck on the old `DEFAULT 'en'`.

**Non-Goals:**
- Generalizing user profile updates (e.g., introducing `UpdateUser` with FieldMask). Out of scope; if a future change needs many mutable user fields, that refactor will subsume the dedicated `UpdatePreferredLanguage`.
- Server-side i18n of emails or Zitadel templates. Tracked separately.
- Auto-detecting language from JWT claims or `Accept-Language` headers. Out of scope.
- Adding more than the two currently supported locales (`ja`, `en`).

## Decisions

### D1. Dedicated `UpdatePreferredLanguage` RPC, not a generic `UpdateUser`

Mirrors the precedent set by the existing `UpdateHome` custom-method RPC. The only currently-mutable user fields are `home` and `preferred_language`; introducing a `FieldMask`-based `UpdateUser` now would be over-engineered and would force a co-migration of `UpdateHome`. If a third mutable field appears, that change can revisit consolidation.

Alternatives considered:
- `UpdateUser(user, update_mask)` (AIP-134 canonical): rejected as over-engineered for two fields, and would require migrating `UpdateHome` simultaneously.
- Reuse `Create`'s idempotent path: rejected — Create's documented contract is "duplicate call is a read, not an upsert"; making one field a write-on-duplicate breaks that contract asymmetrically.

### D2. DB column: drop `DEFAULT 'en'`, NULL out existing rows

The `DEFAULT 'en'` made sense when the field was an internal stub but conflicts with "client decides" semantics. NULL becomes the canonical "not yet set; client must backfill" state. Existing rows are reset to NULL so the client takes responsibility on next hydration — yielding their current effective locale rather than the historical default.

Alternatives considered:
- Leave the default in place and treat `'en'` as both "set by user" and "default": rejected — undistinguishable states block any backfill heuristic.
- Read a one-time legacy `localStorage['language']` at hydration to backfill: rejected — leaves a time-limited compatibility path in the code (the user explicitly wants no localStorage reads while authenticated).

### D3. Proto: `optional string preferred_language` on entity, required `string preferred_language` on `CreateRequest`

On `User`, the field uses `optional` so the wire can distinguish "unset" (NULL in DB) from "explicitly empty" — required for the backfill decision on the frontend. On `CreateRequest`, the field is required (`protovalidate.field.string.min_len = 2`) — the client always knows its current locale and must always send it.

The value is an ISO 639-1 two-letter code (`ja`, `en`). Validation rule: `pattern = "^[a-z]{2}$"`. This keeps room for `ja-JP` style tags in the future via a separate field or a relaxed pattern, but for now Phase-1 supports only base codes.

### D4. Frontend: i18next-browser-languagedetector `caches: ['localStorage']`

The current `caches: []` disables write-back. Switching to `['localStorage']` makes the detector persist its decision after the first navigator-based detection, so subsequent anonymous reloads see a stable language without requiring explicit user action.

Side effect: a `?lang=xx` querystring visit will also be cached. This is intentional — a shared link's language choice should "stick" rather than evaporate. If a user objects, they can change it in Settings.

### D5. Frontend: hydration applies + backfills

After `UserService.Get` completes (in `UserHydrationTask` and in `auth-callback`), the frontend:

1. If `user.preferred_language` is present → `i18n.setLocale(user.preferred_language)`.
2. If absent (legacy NULL row) → call `UpdatePreferredLanguage(i18n.getLocale())` to persist the current effective locale, then keep i18n where it is.
3. In both cases, remove `localStorage['language']` (it served its purpose pre-signup and is no longer read).

The brief flash where the navigator-derived locale is shown before being replaced by the DB value is acceptable per product call. No suspense or splash gate.

### D6. Frontend: anonymous vs authenticated paths in `changeLocale`

Today `changeLocale(i18n, lang)` does `i18n.setLocale + localStorage.setItem`. We split:

- **Anonymous callers** (welcome route, future discovery): unchanged behavior — `setLocale + localStorage.setItem('language', lang)`.
- **Authenticated callers** (settings route): `UpdatePreferredLanguage(lang) → setLocale` — no `localStorage` write.

Concrete implementation can either be (a) two utility functions or (b) one utility that consults `IAuthService.isAuthenticated`. Implementation detail; either is acceptable as long as authenticated callers never touch `localStorage`.

### D7. `Create` continues to ignore home AND preferred_language on idempotent return

The existing contract: "duplicate call is a read, not an upsert; home is ignored on idempotent return". Extending this rule, `preferred_language` is ALSO ignored on idempotent return. The hydration backfill path (D5) handles language for users whose row already exists with NULL.

## Risks / Trade-offs

- **[Existing JA users flip to EN momentarily]** Existing rows with `'en'` are reset to NULL by the migration. On next sign-in, hydration backfills from `i18n.getLocale()`, which is derived from the navigator. If the user's browser is JA, they end up with JA in DB. If their browser is EN but they had explicitly chosen JA in settings (and that choice was lost because we never persisted it server-side anyway), they will see EN and have to switch in Settings once. → Mitigation: documented in release notes; this is a one-time transition cost.

- **[BSR client / backend skew during release]** Adding a required field to `CreateRequest` means a frontend running the old code against a new backend will fail validation, and vice versa. → Mitigation: follow the standard proto-change release order — specification PR → Release → BSR gen → backend & frontend PRs land after. Brief dev/staging skew is acceptable since rollout is coordinated. For prod we time the deploys.

- **[Boot flicker on slow networks]** On authenticated boot, the i18n chain shows JA/EN from navigator first, then switches to the DB value when Get resolves. Could be 200–500ms on cold cache. → Mitigation: accepted per product call (D5). If complaints arise, we can add an AppShell skeleton that masks text until hydration completes.

- **[Settings language change race vs concurrent reload]** User taps language in Settings → UpdatePreferredLanguage in-flight → user hard-reloads before RPC returns. The new value isn't persisted, so the old DB value is read back. → Mitigation: the optimistic UI in Settings shows the change immediately via `i18n.setLocale`; if the RPC fails, we surface a Snack and revert. The hard-reload-mid-flight case is rare and self-correcting (user re-applies).

- **[NULL semantics confusion]** Future readers may not know whether NULL means "legacy unset" or "user opted into 'auto'". → Mitigation: column comment makes the semantics explicit; backfill happens on first hydration so NULL is short-lived per row.

- **[Anonymous users on multiple devices]** Since pre-signup state lives only in `localStorage`, choosing JA on one anonymous device does not affect another. → Out of scope; this is fundamental to anonymous state.

## Migration Plan

1. **specification PR**: proto changes + this OpenSpec change merged.
2. **GitHub Release** on specification: triggers `buf-release.yml` → BSR publishes new schema.
3. **Backend PR**: Atlas migration (`ALTER COLUMN ... DROP DEFAULT`, `UPDATE users SET preferred_language = NULL`), mapper extension, new handler/use-case/repo method, tests. Merged after BSR gen succeeds.
4. **Frontend PR**: detector cache change, entity field, RPC client + service methods, hydration apply/backfill, Settings rewrite, auth-callback cleanup, tests. Merged after backend ships.
5. **Verify in dev**: capture a fresh signed-up user has `preferred_language = 'ja'` (or 'en') in DB; old user signs in → backfill happens; Settings change persists across hard reload.

**Rollback strategy**: revert frontend first (returns to localStorage-only behavior, harmless since DB column still exists and is just unread). Then revert backend if needed (the new RPC and field become unused; Atlas down-migration restores `DEFAULT 'en'` but the existing NULLs can stay — they don't break anything when nothing reads them).

## Open Questions

- Should `Settings → Language` RPC failure revert the UI (pessimistic) or stay applied with a Snack warning (optimistic)? Current preference is optimistic with Snack; finalize in implementation.
- Do we need a Storybook story update for the Settings language-selector to reflect the new RPC-driven state? Decided during apply.
