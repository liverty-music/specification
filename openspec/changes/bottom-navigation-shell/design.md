# Design: Bottom Navigation Shell

## Architecture

```
┌─────────────────────────────────────┐
│           Route Content             │
│                                     │
│   /dashboard  → DashboardPage       │
│   /discover   → DiscoverPage (stub) │
│   /my-artists → MyArtistsPage (stub)│
│   /settings   → SettingsPage (stub) │
│                                     │
├─────────────────────────────────────┤
│  [🏠 Home] [🔍 Discover] [🎸 My Artists] [⚙️ Settings]  │
│           Bottom Navigation Bar     │
└─────────────────────────────────────┘
```

## Component Structure

### BottomNavBar Component

- Fixed to bottom of viewport (`position: fixed; bottom: 0`)
- 4 equally spaced tab items
- Each item: icon + label text
- Active state: accent color highlight, inactive: muted color
- Safe area padding for devices with home indicator (iOS)
- Z-index above page content, below modals/bottom sheets
- Dark themed, consistent with design system

### Conditional Visibility

Reuse the existing conditional navigation logic from `app-shell-layout`:
- **Hidden**: Landing Page, Artist Discovery, Loading Sequence (onboarding flow)
- **Visible**: Dashboard and all post-onboarding routes

### Routing

- Tab switches trigger route navigation (not just component swap)
- URL reflects current tab for deep linking and browser back support
- Default route after onboarding: `/dashboard` (Home tab)

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Navigation type | Bottom Tab Bar | Mobile-first PWA, thumb-reachable, modern standard |
| Top nav bar | Remove or repurpose as header | Bottom nav replaces primary navigation role |
| Tab switching | Route-based | Enables deep linking, browser history, shareable URLs |
| Stub pages | Minimal placeholder with tab title | Allows parallel development of tab content |

## Risks

- **Layout shift**: Adding fixed bottom bar reduces available content height. Dashboard layout may need minor padding adjustment at bottom.
- **Existing top nav**: Need to coordinate removal/simplification of existing top navigation to avoid duplicate navigation patterns.
