# Proposal: Unify User Home Selection UI

## Problem

The user home area selection UI has two separate implementations with inconsistent naming and different interaction patterns:

1. **RegionSetupSheet** (Dashboard/Onboarding) - Flat single-screen with major city quick-select buttons and a prefecture dropdown. Does NOT use the intended 2-step region-to-prefecture flow.
2. **AreaSelectorSheet** (Settings) - Correct 2-step flow (region -> prefecture), but uses "area" naming instead of "home".

The onboarding spec (`frontend-onboarding-flow/spec.md`) was unintentionally written to allow a flat UI ("prefecture dropdown selector or quick-select buttons for major cities"), diverging from the intended 2-step design defined in the settings spec.

Additionally, naming is inconsistent across the codebase: "region", "area", "home", "city" are used interchangeably for the same concept.

## Goals

1. **Unify to a single component** (`user-home-selector`) that implements the 2-step region -> prefecture flow everywhere.
2. **Preserve quick-select** major city buttons as a UX shortcut in Step 1 (tapping a city skips Step 2 and confirms immediately).
3. **Standardize naming** to "user home" / "home area" across components, files, i18n keys, and UI text.
4. **Update all related specs** to reflect the unified 2-step UI and consistent terminology.

## Scope

### Specification (this repo)

| File | Change |
|------|--------|
| `specs/frontend-onboarding-flow/spec.md` | Rewrite "Just-in-Time Region Configuration" to specify 2-step UI with quick-select in Step 1 |
| `specs/settings/spec.md` | Rename "My Area Preference" to "My Home Area", align terminology |
| `specs/user-home/spec.md` | Align localStorage key references and terminology |

### Frontend

| Before | After |
|--------|-------|
| `region-setup-sheet/` component | Deleted (merged into `user-home-selector/`) |
| `area-selector-sheet/` component | Deleted (merged into `user-home-selector/`) |
| (new) | `user-home-selector/` component |
| i18n keys: `region.*`, `areaSelector.*` | `userHome.*` |
| Settings label: "My Area" | "My Home Area" |
| Dashboard label: "My City" | "Home Area" |
| Callback: `onRegionSelected` / `onAreaSelected` | `onHomeSelected` |

### Not in scope

- Backend (proto `Home` message and `UpdateHome` RPC are already correctly named)
- `REGION_GROUPS` constant name (stays as-is; "region" means geographic grouping)
- localStorage key `guest.home` (already correct)

## Unified Component Design

```
UserHomeSelector (BottomSheet dialog)

Step 1:
+------------------------------------------+
|  "Select Your Home Area"                 |
|  "Find live events near you"             |
|                                          |
|  QUICK SELECT                            |
|  [Tokyo] [Osaka] [Nagoya]               |
|  [Fukuoka] [Sapporo] [Sendai]           |
|                                          |
|  SELECT BY REGION                        |
|  [Hokkaido]  [Tohoku]  [Kanto]          |
|  [Chubu]     [Kinki]   [Chugoku]       |
|  [Shikoku]   [Kyushu]                   |
+------------------------------------------+
       |                    |
       | city tap           | region tap
       v                    v
  -> confirm           Step 2:
  -> close             +---------------------------+
                       |  [<- Back]   "Kanto"      |
                       |                           |
                       |  [Tokyo]    [Kanagawa]    |
                       |  [Saitama]  [Chiba]       |
                       |  [Ibaraki]  [Tochigi]     |
                       |  [Gunma]                  |
                       +---------------------------+
                              |
                              | prefecture tap
                              v
                         -> confirm
                         -> close
```

## Risks

- **Two-component merge** requires careful test coverage to ensure both Dashboard and Settings integration points work correctly after unification.
- **i18n key migration** must cover all locales (en, ja) and ensure no orphaned keys remain.
