## Context

Venue `admin_area` is stored as free-text Japanese strings ("東京", "愛知県") with inconsistent formatting. The user's geographic preference is only in localStorage. This blocks internationalization and causes fragile frontend hacks (`s.replace(/[県都道府]$/, '')`) for dashboard lane assignment.

The current data flow: Gemini outputs free-text → stored as-is in DB → frontend normalizes for comparison. The user's preference is set via `RegionSetupSheet` → `localStorage(user.adminArea)` → read by `assignLane()`.

## Goals / Non-Goals

**Goals:**
- Standardize `Venue.admin_area` to ISO 3166-2 codes across all layers
- Persist user home area server-side via `User.home` field and `UpdateHome` RPC
- Rename dashboard lanes to `home / nearby / away` with ISO code comparison
- Migrate existing DB data from free-text to ISO 3166-2
- Maintain Gemini prompt stability (no changes to LLM prompts)

**Non-Goals:**
- Multi-area support for users (selecting multiple home areas)
- `admin_area_level_2` / sub-area support (future phase for US expansion)
- Nearby/adjacency calculation logic (lane 2 currently shows all non-home areas; adjacency is a separate future change)
- Guest user home persistence (guests continue using localStorage until sign-up)

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

### Decision 3: `User.home` as a new Proto field, not reusing admin_area

**Choice**: Add `Home home = 6` to the `User` message. `Home` is a new value-object message wrapping an ISO 3166-2 code string.

**Rationale**: `admin_area` describes an objective geographic attribute of a venue. `home` describes a user's subjective preference. Different naming prevents conflation. The `Home` wrapper message follows the existing VO pattern (like `UserId`, `UserEmail`).

### Decision 4: Dedicated `UpdateHome` RPC

**Choice**: Add `UpdateHome(UpdateHomeRequest) returns (UpdateHomeResponse)` to `UserService` rather than extending the general `Create` flow.

**Rationale**: Home selection happens at a distinct UX moment (onboarding area setup or settings change), separate from account creation. A dedicated RPC keeps concerns separate, enables targeted validation, and avoids bloating `CreateRequest` with optional fields. Follows Google AIP custom method pattern.

### Decision 5: Frontend display via ISO 3166-2 library

**Choice**: Use an npm ISO 3166-2 package to convert codes to localized display names at render time based on `navigator.language`.

**Rationale**: Avoids maintaining translation dictionaries. The i18n display is a pure frontend concern—backend only stores and transmits codes.

### Decision 6: Lane rename — `home / nearby / away`

**Choice**: Rename lane identifiers from `main/region/other` to `home/nearby/away` throughout the codebase.

**Rationale**: Aligns with domain language established in explore session. "Home" and "Away" are natural terms in the live music context. `nearby` serves as a placeholder for future adjacency logic (for now, all non-home events with an admin_area go to `nearby`).

## Risks / Trade-offs

- **[Gemini outputs unknown admin_area text]** → Normalization function returns `nil`; venue stored with `admin_area = NULL`. This is safe—existing behavior treats NULL as "unknown". No data loss.
- **[Existing data migration misses edge cases]** → Migration uses a comprehensive JP prefecture lookup table. Any unmapped values are set to NULL with a log. A dry-run query can be run first to audit.
- **[ISO 3166-2 code changes]** → Extremely rare (last JP change: never). If a code changes, a simple DB migration updates it. Risk is negligible.
- **[Breaking Proto change on AdminArea semantics]** → The `AdminArea.value` field type remains `string`; only the documented value format changes. Wire-compatible, but clients must be updated to handle codes instead of display text. Coordinated frontend+backend deploy required.

## Migration Plan

1. **Proto changes**: Add `Home` message to `user.proto`, `UpdateHome` RPC to `user_service.proto`, update `AdminArea` documentation to specify ISO 3166-2 format.
2. **Backend normalization package**: Implement `normalizeAdminArea()` with JP prefecture lookup table.
3. **DB migration (users)**: `ALTER TABLE users ADD COLUMN home TEXT` with ISO 3166-2 constraint.
4. **DB migration (venues)**: Convert existing free-text `admin_area` to ISO 3166-2 codes using UPDATE with CASE expression.
5. **Backend integration**: Wire normalization into Gemini pipeline post-processing; update venue enrichment search to convert code→text for API queries; implement `UpdateHome` handler.
6. **Frontend integration**: Replace localStorage region storage with `UpdateHome` RPC; update lane logic to use ISO code comparison; add ISO→display name conversion.
7. **Deploy**: Backend first (backward-compatible), then frontend.

## Open Questions

- None at this time. Key decisions were resolved during the explore session.
