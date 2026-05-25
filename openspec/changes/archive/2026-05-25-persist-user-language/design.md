## Context

`app.users.preferred_language` exists in the DB with `DEFAULT 'en'` and the Go `entity.User.PreferredLanguage` field is populated by the repository — but the proto layer never exposes it. As a result, the only effective store for the user's language preference is browser `localStorage` written by `changeLocale()` (`frontend/src/util/change-locale.ts`).

Symptom observed in production: after switching language in Settings, a hard reload occasionally falls back to EN. The likely surfaces are localStorage volatility (Safari ITP cap, private browsing, cross-device divergence) and the absence of any server-side fallback. The only durable fix is to make the backend the source of truth once an account exists.

Pre-signup, the user is anonymous — the only place to remember a language choice is the browser. The existing i18next-browser-languagedetector chain (`['querystring', 'localStorage', 'navigator']`) is correct, but `caches: []` means navigator-detected values are NOT persisted, so each reload re-detects from `navigator.language` instead of remembering a stable choice.

**Post-merge revision (2026-05-23).** Prod verification after this change shipped surfaced a latent backend bug that the migration triggered:

- `UserRepository.scanUser` scanned the nullable `preferred_language` column directly into `*string`. With `DEFAULT 'en'` in place every existing row had a value, so the bug was invisible. The migration's `UPDATE users SET preferred_language = NULL WHERE preferred_language IS NOT NULL` flipped every existing row to NULL; `pgx` then rejected `Scan` for every subsequent `Get` / `GetByExternalID` / `List` call on those rows.
- PR #304 incidentally added the right fix (`sql.NullString` + `nullStringFromEmpty`) but the backend release carrying it has not yet reached prod, which still runs `v1.1.0`. Prod hydration is therefore broken for all existing users until that release lands.
- `users.country` and `users.time_zone` are nullable in DB and remain raw `string` scans even on origin/main. Today every row has a value so the bug does not fire, but the next migration that introduces NULLs anywhere in those columns will recreate the incident.
- `userUseCase.Create`'s idempotent retry collapses every `GetByExternalID` error into "row not found → propagate original AlreadyExists". A scan failure therefore surfaces to the client as `AlreadyExists`, masking the actual fault and making this incident much harder to root-cause.

These three observations are folded into the design below as D8, D9, and D10. The original schema/RPC decisions (D1–D7) remain unchanged.

## Goals / Non-Goals

**Goals:**
- Make `users.preferred_language` the single source of truth for authenticated users.
- Capture the pre-signup effective locale at Create time and persist it.
- Persist navigator-detected locale to `localStorage` on first visit so anonymous reload behavior is stable.
- After signup, remove `localStorage['language']` and never read it again while signed in.
- Provide a backfill path for legacy rows so they aren't permanently stuck on the old `DEFAULT 'en'`.
- **(added)** Make `UserRepository` NULL-safe across every nullable `users` column so a future migration cannot retrigger this incident.
- **(added)** Make `userUseCase.Create`'s idempotent retry surface the actual error class instead of collapsing every retry failure into AlreadyExists.

**Non-Goals:**
- Generalizing user profile updates (e.g., `UpdateUser` with FieldMask). If a future change needs many mutable user fields, that refactor will subsume `UpdatePreferredLanguage`.
- Server-side i18n of emails or Zitadel templates.
- Auto-detecting language from JWT claims or `Accept-Language` headers.
- Adding more than the two currently supported locales (`ja`, `en`).
- Refactoring scan-NULL safety across other entities (`concerts`, `events`, etc.). Out of scope; this change only addresses the `users` table because that is where the incident landed. A follow-up housekeeping change can extend the same pattern repo-wide.

## Decisions

### D1. Dedicated `UpdatePreferredLanguage` RPC, not a generic `UpdateUser`

Mirrors `UpdateHome`. The only currently-mutable user fields are `home` and `preferred_language`; introducing a `FieldMask`-based `UpdateUser` now would be over-engineered and would force a co-migration of `UpdateHome`. If a third mutable field appears, that change can revisit consolidation.

Alternatives considered:
- `UpdateUser(user, update_mask)` (AIP-134 canonical): rejected as over-engineered for two fields, and would require migrating `UpdateHome` simultaneously.
- Reuse `Create`'s idempotent path: rejected — Create's documented contract is "duplicate call is a read, not an upsert"; making one field a write-on-duplicate breaks that contract asymmetrically.

### D2. DB column: drop `DEFAULT 'en'`, NULL out existing rows

The `DEFAULT 'en'` made sense when the field was an internal stub but conflicts with "client decides" semantics. NULL becomes the canonical "not yet set; client must backfill" state. Existing rows are reset to NULL so the client takes responsibility on next hydration — yielding their current effective locale rather than the historical default.

Alternatives considered:
- Leave the default in place and treat `'en'` as both "set by user" and "default": rejected — undistinguishable states block any backfill heuristic.
- Read a one-time legacy `localStorage['language']` at hydration to backfill: rejected — leaves a time-limited compatibility path in the code (the user explicitly wants no localStorage reads while authenticated).

### D3. Proto: `optional string preferred_language` on both `User` and `CreateRequest`

On `User`, `optional` lets the wire distinguish "unset" (NULL in DB) from "explicitly empty" — required for the backfill decision on the frontend.

On `CreateRequest`, also `optional` to keep the RPC backward-compatible during a rolling deploy where the new backend may briefly serve old frontend clients. Updated clients SHALL always send the value; old clients that omit it produce rows with NULL `preferred_language` and hit the same backfill path as legacy rows — no extra code surface.

For `UpdatePreferredLanguageRequest`, the field is required (plain `string`) — there is no transition concern since the RPC is brand new; any caller MUST be from updated code.

Validation when present: `min_len: 2` and `pattern: "^[a-z]{2}$"`. Phase-1 supports `ja` and `en` only.

### D4. Frontend: i18next-browser-languagedetector `caches: ['localStorage']`

`caches: []` disables write-back. `['localStorage']` makes the detector persist its decision after the first navigator-based detection, so anonymous reloads see a stable language. Side effect: `?lang=xx` querystring visits also cache. Intentional — a shared link's language choice should stick.

### D5. Frontend: hydration applies + backfills

After `UserService.Get` completes:

1. If `user.preferred_language` is present → `i18n.setLocale(user.preferred_language)`.
2. If absent (legacy NULL row) → call `UpdatePreferredLanguage(i18n.getLocale())` and keep i18n where it is.
3. In both cases, remove `localStorage['language']`.

The brief flash where the navigator-derived locale is shown before being replaced by the DB value is acceptable per product call.

### D6. Frontend: anonymous vs authenticated paths in `changeLocale`

Today `changeLocale(i18n, lang)` does `setLocale + localStorage.setItem`. Split:

- Anonymous (welcome, future discovery): unchanged — `setLocale + localStorage.setItem`.
- Authenticated (settings): `UpdatePreferredLanguage(lang) → setLocale`, NO `localStorage` write.

Implementation can be two utility functions OR one utility consulting `IAuthService.isAuthenticated`. Either is acceptable as long as authenticated callers never touch `localStorage`.

### D7. `Create` ignores `home` AND `preferred_language` on idempotent return

Extending the existing rule: a duplicate Create is a read. The hydration backfill path (D5) handles language for users whose row already exists with NULL.

### D8. Repo: scan every nullable `users` column through `sql.NullString` (added 2026-05-23)

Direct scans of nullable columns into Go `string` are a pgx-level crash waiting for a NULL value to land. We adopt a uniform pattern:

- Every nullable column in `users` (`preferred_language`, `country`, `time_zone`, `safe_address`) is scanned into a `sql.NullString` local first, then assigned to the entity field via `.String` when `.Valid`. Entity fields stay typed as `string` because every consumer treats the Go zero value (empty string) as "absent"; this keeps call sites unchanged.
- A `nullStringFromEmpty(s string) sql.NullString` write-boundary helper is used on INSERT/UPDATE so the Go-side `""`-as-absent convention round-trips to SQL NULL.
- `SELECT` lists do NOT use `COALESCE(..., '')` as the protection mechanism. Reasoning: COALESCE masks the distinction between NULL and empty-string at the wire boundary, which we need elsewhere (the proto layer omits the field when the row is NULL). Scanning into `sql.NullString` preserves the distinction while still defending against the crash.

Alternatives considered:
- Change entity field type to `*string` or `sql.NullString`: rejected as a much wider refactor (every caller of `user.PreferredLanguage` would need handling). The intermediate-local approach localizes the fix to the repo.
- Use `COALESCE` only: rejected for the reason above (loses NULL-vs-empty distinction at the wire).
- Add a custom `pgx.ScannerFunc` per entity: rejected as overkill for four columns; the intermediate-local pattern is grep-able and consistent with `homeID/countryCode/level1/level2` already in `scanUser`.

This decision applies retroactively to `preferred_language` (already implemented in PR #304) and forward to `country` and `time_zone` (still raw on origin/main; in scope of this change's task list).

### D9. `userUseCase.Create` retry path: branch on error class, not on boolean (added 2026-05-23)

Current behavior:

```go
existing, getErr := uc.userRepo.GetByExternalID(ctx, params.ExternalID)
if getErr != nil {
    return nil, err  // returns original AlreadyExists
}
return existing, nil
```

Problem: any `getErr` is treated as "row not found by external_id → must be email collision → propagate original AlreadyExists". When the actual error is `Internal` (scan failure, encoding error, OOM) the operator sees a misleading `AlreadyExists` at the wire and the real failure is hidden.

Decision: distinguish error classes:

- `codes.NotFound` → propagate original `AlreadyExists` (email collision case; current contract).
- Any other code (`Internal`, `Unavailable`, scan errors, etc.) → wrap and return the actual `getErr` as the response. The original `AlreadyExists` is logged at WARN level (with both the original and the new errors) so the operator has full context, but the wire response carries the truthful failure.

Alternatives considered:
- Always propagate `getErr`: rejected — loses the legitimate "duplicate-email-different-external-id" signal that callers may want to react to.
- Always log + propagate original: rejected — exactly the masking problem this change exists to fix.

### D10. Migration deploy gate: backend release with D8 fix MUST precede the legacy-row UPDATE (added 2026-05-23)

The migration `20260521083536_drop_users_preferred_language_default.sql` flips every existing row's `preferred_language` to NULL. A backend image whose `scanUser` is not NULL-safe (e.g., prod `v1.1.0` at the time of writing) will then fail every `Get` for those rows.

Decision: the operator runbook for this change SHALL include an explicit pre-flight check:

1. Confirm the target environment's currently-deployed backend image was built from a commit that contains the D8 fix (`grep -q "sql.NullString" internal/infrastructure/database/rdb/user_repo.go`).
2. Only then trigger or merge the Atlas migration.

When the check fails, the operator MUST cut a new backend release and deploy it BEFORE allowing the migration to advance. This is environment-local — dev and prod each enforce independently.

This is a process control, not a code-level lock. We rejected the alternative of a SQL-level guard (e.g., `DO $$ ... SELECT pg_database_setting(...) ... $$`) because Atlas migrations are write-once-immutable; a guard that aborts mid-deploy leaves Atlas in a dirty state that requires manual intervention to clear.

## Risks / Trade-offs

- **[Prod recovery requires a backend release]** Two existing prod users currently see `preferred_language` NULL on disk and Create-already-exists crashes at the wire. The fix path is to deploy the backend release containing PR #304's scan fix; once that lands, the hydration backfill self-heals both rows on next sign-in. → Mitigation: prioritize the release cut; both affected accounts are operator-owned test accounts (no customer impact).

- **[Existing JA users flip to EN momentarily]** Existing rows with `'en'` are reset to NULL by the migration. On next sign-in, hydration backfills from `i18n.getLocale()` (derived from navigator). If the user's browser is JA they end up with JA in DB. If it's EN but they had explicitly chosen JA, they see EN once and must switch in Settings. → Mitigation: documented in release notes; one-time transition cost.

- **[BSR client / backend skew during release]** Adding fields and an RPC means brief skew between schemas during rollout. → Mitigation: standard proto-change release order (specification PR → Release → BSR gen → backend & frontend PRs). All wire changes are additive so old clients keep working.

- **[Boot flicker on slow networks]** On authenticated boot, i18n shows the navigator-detected value first, then switches to the DB value when Get resolves. → Mitigation: accepted per product call.

- **[Settings language change race vs concurrent reload]** Tap language → RPC in-flight → hard reload. The new value isn't persisted, the old DB value is read back. → Mitigation: optimistic UI applies immediately via `setLocale`; if the RPC fails we Snack and revert. The hard-reload-mid-flight case is rare and self-correcting.

- **[NULL semantics confusion]** Future readers may not know whether NULL means "legacy unset" or "user opted into auto". → Mitigation: column comment makes the semantics explicit; backfill happens on first hydration so NULL is short-lived per row.

- **[Latent `country` / `time_zone` recurrence]** Today no row has NULL in either column so the raw `string` scans don't fire. The next migration that introduces NULLs there reopens the same wound. → Mitigation: D8 is applied to all four nullable columns in this change, not just `preferred_language`. Tests in this change must include a NULL-row case for each.

- **[Anonymous users on multiple devices]** Pre-signup state lives only in `localStorage`; choosing JA on one device does not affect another. → Out of scope; fundamental to anonymous state.

## Migration Plan

1. **specification PR**: proto changes + this OpenSpec change merged. ✓ done (`vX.Y.Z`).
2. **GitHub Release** on specification → BSR gen. ✓ done.
3. **Backend PR #304**: Atlas migration, mapper extension, handler / use case / repo, tests. ✓ merged (`392d823`). **Note**: this PR incidentally implemented D8 for `preferred_language` but did NOT extend it to `country` / `time_zone`, and did NOT implement D9. Follow-up work tracked in `tasks.md` §2-post-merge.
4. **Frontend PR #366**: detector cache change, entity field, RPC client + service methods, hydration apply/backfill, Settings rewrite, auth-callback cleanup, tests. ✓ merged (`1ccec98`).
5. **Backend follow-up PR** (NEW): extend D8 scan-NULL safety to `country` and `time_zone`; implement D9 error-class branching in `userUseCase.Create`'s retry path; add `scanUser` tests with NULL-row fixtures. Cut a release after merge.
6. **Prod recovery**: per D10, deploy the new backend release to prod. After deploy, the two existing prod users self-heal via hydration backfill on next sign-in.
7. **Verify in dev**: dev environment is unreachable from operator workstations as of 2026-05-19 (TLS / control-plane endpoint down — tracked separately). Verification SHALL run against prod after step 6 instead of dev. Specific steps in `tasks.md` §5.

**Rollback strategy**:
- Revert frontend first (returns to localStorage-only behavior; harmless since DB column still exists and is just unread).
- Revert backend next if needed (the new RPC and field become unused; the migration is NOT rolled back — leaving NULL rows in place is harmless once the older backend is back because `v1.1.0`-class images would crash and we are reverting AWAY from that state, not toward it).

## Open Questions

- Should the D8 pattern be extended repo-wide (concerts, events, venues) as a separate housekeeping change? Recommendation: yes, but in a follow-up `nullable-scan-safety` change so this one stays scoped to the incident path.
- Should `Settings → Language` RPC failure revert the UI (pessimistic) or stay applied with a Snack warning (optimistic)? Implemented as optimistic with Snack in PR #366; no change needed.
