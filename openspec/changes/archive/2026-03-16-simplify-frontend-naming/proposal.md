## Why

The frontend `routes/` directory has three naming inconsistencies that make navigation and grep difficult:

1. **Redundant `-page` suffix** — Files repeat the concept already expressed by the directory: `routes/discover/discover-page.ts`.
2. **Inconsistent directory nesting** — `dashboard` and `auth-callback` sit flat in `routes/` while all others use subdirectories. `welcome-page` and `about-page` live in `src/` rather than `routes/`.
3. **`discover` vs `discovery` naming split** — The route directory is `discover/`, the i18n has both `"discover"` and `"discovery"` namespaces (with duplicate keys), and class names use `Discover`. The backend uses `discovery` consistently.

## What Changes

- Rename all route component files from `-page` suffix to `-route` suffix (e.g. `discover-page.ts` → `discovery-route.ts`)
- Move `welcome-page`, `about-page` from `src/` into `routes/` subdirectories
- Move `dashboard`, `auth-callback` from flat files into their own `routes/` subdirectories
- Rename `routes/discover/` directory to `routes/discovery/` and update all class names, URL paths, nav references, and icon switch-cases
- Merge i18n `"discover"` namespace into `"discovery"`, deduplicate keys (keep `"discovery"` values for duplicates)
- Update all route class names to use `-Route` suffix (e.g. `DiscoverPage` → `DiscoveryRoute`, `Dashboard` → `DashboardRoute`)

## Capabilities

### Modified Capabilities

- `frontend-landing-page`: Route component file renamed and relocated (`welcome-page` → `routes/welcome/welcome-route`)
- `bottom-navigation-shell`: Nav path updated from `discover` to `discovery`
- `artist-discovery-ui`: Directory, class, i18n namespace unified to `discovery`

## Impact

- **Frontend**: File moves, class renames, i18n namespace merge, URL path change (`/discover` → `/discovery`)
- **Backend**: No changes
- **Protobuf/API**: No changes
- **Database**: No changes
- **Infrastructure**: No changes
- **Breaking URL change**: `/discover` → `/discovery` (acceptable — app is pre-launch, no external links exist)
