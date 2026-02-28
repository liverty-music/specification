## Context

Venue `admin_area` is stored as free-text Japanese strings ("東京", "愛知県") with inconsistent formatting. The user's geographic preference is only in localStorage. This blocks internationalization and causes fragile frontend hacks (`s.replace(/[県都道府]$/, '')`) for dashboard lane assignment.

The current data flow: Gemini outputs free-text → stored as-is in DB → frontend normalizes for comparison. The user's preference is set via `RegionSetupSheet` → `localStorage(user.adminArea)` → read by `assignLane()`.

## Goals / Non-Goals

**Goals:**
- Standardize `Venue.admin_area` to ISO 3166-2 codes across all layers
- Persist user home area server-side via structured `User.home` field and RPC
- Support atomic home persistence at account creation (onboarding flow)
- Rename dashboard lanes to `home / nearby / away` with ISO code comparison
- Migrate existing DB data from free-text to ISO 3166-2
- Maintain Gemini prompt stability (no changes to LLM prompts)
- Design an extensible Home structure that supports future sub-area granularity (e.g., US county level)

**Non-Goals:**
- Multi-area support for users (selecting multiple home areas)
- Nearby/adjacency calculation logic (lane 2 currently shows all non-home areas; adjacency is a separate future change)
- Guest user home persistence (guests continue using localStorage until sign-up)
- Implementing level_2 finer granularity (Phase 1 is Japan-only with level_1 only; the schema supports level_2 but it is not populated)

## Decisions

### Decision 1: ISO 3166-2 as canonical admin_area representation

**Choice**: Use ISO 3166-2 subdivision codes (e.g., `JP-13` for Tokyo, `JP-40` for Fukuoka) as the canonical stored value.

**Alternatives considered**:
- English lowercase names (`"tokyo"`, `"fukuoka"`): Human-readable but requires maintaining a custom dictionary; ambiguous for international names.
- Google Place IDs: Vendor lock-in; Place IDs represent points, not administrative subdivisions.
- Numeric codes only (`13`, `40`): Lose country prefix; ambiguous across countries.

**Rationale**: ISO 3166-2 is the international standard, unambiguous, well-supported by libraries in both Go and JS/TS ecosystems, and naturally extends to other countries without custom dictionaries.

### Decision 2: Backend normalization, not LLM prompt change

**Choice**: Keep Gemini prompts outputting free-text admin_area. Add a `normalizeAdminArea(text) → ISO code | nil` function in the backend pipeline.

**Rationale**: LLMs are reliable at text inference ("Zepp Nagoya" → "愛知県") but unreliable at code recall (JP-23 vs JP-24). A deterministic lookup table is 100% accurate. No token cost increase. The normalization function handles variants: "東京", "東京都", "Tokyo", "tokyo" → `JP-13`.

### Decision 3: Structured Home with hierarchical levels

**Choice**: `Home` is a structured proto message with three fields: `country_code` (ISO 3166-1 alpha-2), `level_1` (ISO 3166-2 subdivision), and an optional `level_2` (country-specific finer area code).

**Alternatives considered**:
- Single ISO 3166-2 string (`"JP-13"`): Simpler but cannot represent finer granularity; a future US county-level need would require a breaking schema change and data migration.
- Polymorphic `subdivision` column with `scheme` discriminator: Flexible but adds complexity; the scheme × country matrix grows unpredictably.
- URI-style identifier (`"iso3166-2:JP-13"`): Over-engineered; requires parsing on every read; no query advantage.
- Hierarchical path (`["JP", "JP-13"]`): Flexible but parsing-heavy; PostgreSQL array queries are slower than column equality.

**Rationale**: The structured approach avoids the Polymorphic Column anti-pattern. `level_1` is always ISO 3166-2 worldwide (fixed contract). `level_2` code system is a discriminated union keyed by `country_code` — meaning `(country_code, level_2)` unambiguously determines the code system (US→FIPS, DE→AGS). Each column has a single, well-defined semantic. `country_code` is redundant with the `level_1` prefix but enables efficient `WHERE country_code = ?` queries and avoids string parsing.

### Decision 4: Normalized `homes` table, not inline columns

**Choice**: Create a separate `homes` table with `id`, `country_code`, `level_1`, and `level_2`. The `users` table references it via `home_id` FK.

**Alternatives considered**:
- Inline columns on `users` table (`home_country_code`, `home_level_1`, `home_level_2`): Fewer JOINs, but spreads home logic across the users table; harder to extend if home gains additional attributes (e.g., display preferences, coordinates for nearby calculation).

**Rationale**: A normalized `homes` table keeps the home concept self-contained, makes it reusable if other entities need a home reference in the future, and aligns with the entity's structured proto representation.

### Decision 5: Home included in CreateRequest for atomic onboarding

**Choice**: Add an optional `Home home` field to `CreateRequest`, so the home area selected during onboarding is persisted atomically with account creation.

**Alternatives considered**:
- Separate `UpdateHome` call after `Create`: Requires two RPCs with a race/failure window; guest home in localStorage could be lost if `UpdateHome` fails after `Create` succeeds.
- Merge service syncs home during guest-data merge: The merge service currently handles only artist follows; adding home to it is possible but couples home persistence to an unrelated merge operation.

**Rationale**: The onboarding flow selects home before sign-up. Including it in `Create` makes the operation atomic — no partial state where a user exists without their home. `UpdateHome` remains available for later changes from settings.

### Decision 6: Dedicated `UpdateHome` RPC

**Choice**: Add `UpdateHome(UpdateHomeRequest) returns (UpdateHomeResponse)` to `UserService` for post-creation home changes.

**Rationale**: Home changes from settings happen at a distinct UX moment, separate from account creation. A dedicated RPC keeps concerns separate, enables targeted validation, and avoids bloating a general "update profile" RPC.

### Decision 7: Frontend display via ISO 3166-2 lookup map

**Choice**: Use a local TypeScript lookup map (`iso3166.ts`) to convert codes to localized display names at render time based on `navigator.language`.

**Rationale**: Avoids maintaining translation dictionaries as a separate package. The i18n display is a pure frontend concern—backend only stores and transmits codes. Phase 1 covers all 47 Japanese prefectures.

### Decision 8: Lane rename — `home / nearby / away`

**Choice**: Rename lane identifiers from `main/region/other` to `home/nearby/away` throughout the codebase.

**Rationale**: Aligns with domain language established in explore session. "Home" and "Away" are natural terms in the live music context. `nearby` serves as a placeholder for future adjacency logic (for now, all non-home events with an admin_area go to `nearby`).

### Decision 9: Lane assignment granularity follows Home precision

**Choice**: Lane comparison uses the finest available level. When `level_2` is set on the user's home, compare at `level_2` granularity. When only `level_1` is set, compare at `level_1`.

**Rationale**: This allows Japan users (level_1 only) and future US users (level_2 county) to have appropriate lane classification without code changes — only the data granularity changes.

## Risks / Trade-offs

- **[Gemini outputs unknown admin_area text]** → Normalization function returns `nil`; venue stored with `admin_area = NULL`. This is safe—existing behavior treats NULL as "unknown". No data loss.
- **[Existing data migration misses edge cases]** → Migration uses a comprehensive JP prefecture lookup table. Any unmapped values are set to NULL with a log. A dry-run query can be run first to audit.
- **[ISO 3166-2 code changes]** → Extremely rare (last JP change: never). If a code changes, a simple DB migration updates it. Risk is negligible.
- **[Breaking Proto change on Home message]** → The `Home` message field numbers change from `value = 1` to `country_code = 1, level_1 = 2, level_2 = 3`. This is a wire-incompatible change, but the feature is not yet deployed to production. All consumers (backend, frontend) are updated in the same release.
- **[Normalized homes table adds JOIN complexity]** → The `users` ← `homes` JOIN is a simple FK lookup on a small table. The performance impact is negligible. The benefit of a self-contained home entity outweighs the extra JOIN.
- **[level_2 code system varies by country]** → Documented as a discriminated union in the proto comment. Validation logic can branch on `country_code`. Phase 1 never uses `level_2`, so no immediate validation burden.

## Migration Plan

1. **Proto changes**: Restructure `Home` message with `country_code`, `level_1`, `level_2`; add optional `home` to `CreateRequest`; update `UpdateHome` RPC docs.
2. **Backend normalization package**: Implement `normalizeAdminArea()` with JP prefecture lookup table; add `CountryCode()` extraction helper.
3. **DB migration (homes table)**: `CREATE TABLE homes (id, country_code, level_1, level_2)`; `ALTER TABLE users ADD COLUMN home_id TEXT REFERENCES homes(id)`; migrate existing `users.home` text values to `homes` records.
4. **DB migration (venues)**: Convert existing free-text `admin_area` to ISO 3166-2 codes using UPDATE with CASE expression.
5. **Backend integration**: Wire normalization into Gemini pipeline post-processing; update venue enrichment search to convert code→text for API queries; implement `UpdateHome` handler; update `Create` handler to accept optional home; update mapper/entity for structured Home.
6. **Frontend integration**: Update `CreateRequest` to include home from onboarding; replace localStorage region storage with RPC; update lane logic for structured Home comparison; add ISO→display name conversion.
7. **Deploy**: Backend first (backward-compatible), then frontend.

## Open Questions

- None at this time. Key decisions were resolved during the explore session.
