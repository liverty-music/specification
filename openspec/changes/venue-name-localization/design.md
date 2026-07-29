## Context

The concert data pipeline currently stores two venue name representations:
- `venue.name` — canonical name fetched from Google Places API (stored without `languageCode`, so often English: "Nippon Budokan")
- `listed_venue_name` — verbatim name scraped by Gemini from the artist's official site (typically Japanese for Japanese artists: "日本武道館"), stored raw with possible prefecture prefixes ("大阪・フェスティバルホール")

The frontend mapper unconditionally selects `venue.name ?? listed_venue_name`, so Japanese users see English names when Places returns an English canonical.

No schema change is needed: both fields are already in the proto and accessible on the frontend.

## Goals / Non-Goals

**Goals:**
- Japanese users (`preferredLanguage = ja`) see Japanese venue names where available.
- English users (`preferredLanguage = en`) see English venue names where available.
- New venues are stored with a locale-appropriate canonical name from Places.
- `listed_venue_name` is clean (no prefecture prefix noise) when it reaches the frontend.

**Non-Goals:**
- Backfilling existing venues that were stored with English canonical names.
- Adding new proto fields (no BSR gen cycle).
- Supporting languages other than `ja` and `en` (Korean, Chinese, etc. get English fallback for now).
- Perfect English coverage for venues that only have Japanese `listed_venue_name` and no `venue.name`.

## Decisions

### Decision 1: Use `listed_venue_name` as the Japanese display name, `venue.name` as English

**Choice**: For `lang=ja`, prefer `listed_venue_name`; for `lang=en`, prefer `venue.name`. Cross-fallback in both directions.

**Why**: `listed_venue_name` is scraped from the artist's Japanese official site — it is the most reliable Japanese source. `venue.name` from Places (once `languageCode` is fixed) will be locale-appropriate for new venues. The two fields naturally complement each other.

**Alternative considered**: Add `name_en` / `name_ja` fields to the Venue proto. Rejected: requires schema change, BSR gen cycle, migration, and backfill — disproportionate cost for the immediate problem.

**Alternative considered**: Pass `Accept-Language` header from frontend and have backend select the name per request. Rejected: adds per-request dynamic selection complexity; the data is already available in both representations on the wire.

### Decision 2: Derive `languageCode` from the venue's country code (extracted from `admin_area`)

**Choice**: Extract the ISO 3166-1 alpha-2 country code from `admin_area` (e.g., `"JP-13"` → `"JP"`), map to a BCP 47 language tag via a small static switch, and pass it as `languageCode` to the Places API `textSearch` request body.

```
JP → "ja"
KR → "ko"
CN → "zh-CN"
TW → "zh-TW"
default → "en"
```

**Why**: The mapping is a small, stable static table (~5 entries cover the realistic venue distribution). The country code is already present in `admin_area` at call time. No external lookup needed.

**Alternative considered**: Hardcode `languageCode: "ja"` for all venues. Acceptable as a fallback but incorrect for future international concerts.

**Why not** use the user's `preferredLanguage`: venue names should reflect the venue's locale, not the viewer's. A Japanese venue should return a Japanese name regardless of who is viewing.

### Decision 3: Normalize `listed_venue_name` before storage, not only at dedup time

**Choice**: Apply `entity.NormalizeVenueName()` to `sc.ListedVenueName` in `concert_creation_uc.go` before building the `StagedConcert`, so the stored value is already clean.

**Why**: `NormalizeVenueName` is already used for dedup key computation. Moving it to the storage path means the frontend can use `listed_venue_name` as a display value directly, without needing to re-implement the normalization logic in TypeScript.

**Idempotency**: `NormalizeVenueName` is idempotent, so dedup comparisons (`NormalizeVenueName(stored)`) remain correct.

**Side effect**: `venues.listed_venue_name` (the fallback lookup key used in `GetByListedName`) will also be stored in normalized form. This is consistent because both the stored key and any future query through the same path are normalized identically.

### Decision 4: Pass `lang` to the concert mapper as a parameter

**Choice**: Add a `lang: string` parameter to the mapper function (or the mapper class constructor, whichever the existing pattern uses). Callers obtain the value from `UserStore.currentLanguage` (or equivalent DI).

**Why**: Pure function / thin adapter — mapper should not reach into stores directly. Passing `lang` keeps the mapper testable without mocking the store.

## Risks / Trade-offs

- **Existing English-named venues** — Venues already in the DB with an English `venue.name` and a populated `listed_venue_name` will render correctly for `ja` users via the fallback. Venues with a null `listed_venue_name` will remain in English until re-resolved (acceptable until a future backfill pass).
- **`listed_venue_name` null rate** — If a concert has no `listed_venue_name` (e.g., hand-entered or legacy data), the `lang=ja` path falls back to `venue.name`. This gracefully degrades to the current behavior.
- **Places API language quality** — Google Places does not always return a localized name; some venues have only an English entry even in the `ja` response. The frontend fallback handles this.
- **Normalization changes stored keys** — Storing normalized `listed_venue_name` means the `GetByListedName` lookup key changes for future concerts. Existing DB rows retain their raw (unnormalized) values, so a new concert with a normalized listed name that matches an old raw name will miss the DB cache and re-hit Places. This is a one-time inefficiency, not a correctness issue.

## Migration Plan

1. Deploy backend change (normalize before storage + languageCode in Places API). New venues from this point onward are stored correctly.
2. Deploy frontend change (locale-aware mapper). Immediately takes effect for all concerts using the existing `listed_venue_name` data.
3. No migration script required for existing rows. Existing venues with English `venue.name` are covered by the frontend `listed_venue_name` fallback.

Rollback: both backend and frontend changes are independently safe to revert. Backend revert restores previous Places API behavior (no `languageCode`). Frontend revert restores `venue.name ?? listed_venue_name` priority.
