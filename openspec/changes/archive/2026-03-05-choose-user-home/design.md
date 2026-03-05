## Context

The user's home area selection is implemented by two separate Aurelia 2 components with different UX patterns and inconsistent naming:

- **RegionSetupSheet** (Dashboard/Onboarding): Flat single-screen with major city quick-select buttons + a prefecture `<select>` dropdown. No region grouping step.
- **AreaSelectorSheet** (Settings): Correct 2-step region -> prefecture selection flow.

Both components perform the same operation: persist an ISO 3166-2 code via `UserService.updateHome()` (authenticated) or `localStorage` (guest). The split was unintentional and the onboarding spec diverged from the intended 2-step design.

Naming is fragmented: "region", "area", "home", "city" are used interchangeably for the same domain concept across component names, callbacks, i18n keys, and UI labels.

## Goals / Non-Goals

**Goals:**
- Merge `RegionSetupSheet` and `AreaSelectorSheet` into a single `UserHomeSelector` component with 2-step flow
- Integrate quick-select cities into Step 1 of the unified component
- Standardize all naming to "user home" / "home area" in code and UI
- Update specs to match the unified behavior

**Non-Goals:**
- Changing the backend proto model (`Home` message, `UpdateHome` RPC) — already named correctly
- Renaming `REGION_GROUPS` constant — "region" correctly means geographic grouping
- Changing the localStorage key `guest.home` — already correct
- Redesigning the visual/CSS treatment (keep existing BottomSheet dialog pattern)

## Decisions

### 1. Single component with unified 2-step flow

**Decision**: Create `user-home-selector/` component, delete both `region-setup-sheet/` and `area-selector-sheet/`.

**Rationale**: Both components share identical persistence logic (auth check -> RPC or localStorage). The only behavioral difference is the selection UI, which was an unintended spec divergence. A single component eliminates duplication and ensures consistent UX.

**Alternative considered**: Keep two components, fix `RegionSetupSheet` to use 2-step flow. Rejected because the components would then be functionally identical with different names.

### 2. Quick-select cities in Step 1 alongside region buttons

**Decision**: Step 1 shows quick-select major city buttons above the region grid. Tapping a city confirms immediately (skips Step 2). Tapping a region transitions to Step 2 (prefecture list).

**Rationale**: Quick-select improves onboarding speed for users in major metropolitan areas (covers ~60% of Japan's population). Placing it in Step 1 gives it prominence without requiring an extra screen.

**Alternative considered**: Remove quick-select entirely and force all users through 2-step. Rejected because it degrades UX for majority of users.

### 3. i18n key consolidation under `userHome.*`

**Decision**: Consolidate `region.*` and `areaSelector.*` i18n keys under `userHome.*`. Structure:

```
userHome:
  title: "Select Your Home Area"
  description: "Find live events near you"
  quickSelect: "Quick Select"
  selectByRegion: "Select by Region"
  back: "Back"
  regions:
    hokkaido: ...
    tohoku: ...
  prefectures:
    hokkaido: ...
    aomori: ...
  cities:
    tokyo: ...
    osaka: ...
```

**Rationale**: Consolidating under a single namespace eliminates the current confusion where `region.title` says "Tell Us Your Area" and `areaSelector.title` says "Change My Area". Both are the same component now.

**Alternative considered**: Keep `region.*` namespace, rename to `home.*`. Rejected because `region.*` is overloaded (means both "user's location" and "geographic grouping") and `home` alone is ambiguous in i18n context.

### 4. Callback and method naming: `onHomeSelected`

**Decision**: The unified component exposes `@bindable onHomeSelected` callback. Static method: `UserHomeSelector.getStoredHome()`.

**Rationale**: Aligns with backend naming (`User.home`, `updateHome()`). The callback name makes clear that the full selection process is complete, not just a region or area step.

### 5. Settings label: "My Home Area"

**Decision**: Rename the Settings row label from "My Area" (`settings.myArea`) to "My Home Area" (`settings.myHomeArea`).

**Rationale**: "Home Area" is more specific than "Area" and matches the domain language used in the proto definition and product design docs.

### 6. Dashboard header labels

**Decision**: Rename `dashboard.header.myCity` to `dashboard.header.homeArea` and keep `dashboard.header.region` as-is (it refers to the "Nearby" lane, which is a different concept).

**Rationale**: "My City" is misleading — the user selects a prefecture, not a city. "Home Area" aligns with the unified naming. The "region" header for the Nearby lane is a separate concept (geographic proximity) and is not part of this change.

## Risks / Trade-offs

**[Risk] i18n key rename breaks runtime translations** -> Mitigation: Grep all `.html` and `.ts` files for old key patterns (`region.title`, `areaSelector.*`, `settings.myArea`) and replace exhaustively. Both `en` and `ja` locale files must be updated atomically.

**[Risk] Two integration points (Dashboard + Settings) may have different expectations** -> Mitigation: The component accepts the same `@bindable onHomeSelected` callback. Dashboard uses it to trigger lane population; Settings uses it to refresh the display. Both receive an ISO code string — no behavioral difference.

**[Risk] Orphaned CSS classes from deleted components** -> Mitigation: Each component has its own scoped CSS file. Deleting the component directories removes the CSS automatically.
