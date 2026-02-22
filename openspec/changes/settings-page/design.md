# Design: Settings Page

## UI Structure

```
┌─────────────────────────────────┐
│  ⚙️ Settings                    │
├─────────────────────────────────┤
│                                 │
│  PREFERENCES                    │
│  ┌─────────────────────────┐   │
│  │ 📍 My Area        関東 > │   │
│  ├─────────────────────────┤   │
│  │ 🔔 Notifications   [ON] │   │
│  └─────────────────────────┘   │
│                                 │
│  ABOUT                          │
│  ┌─────────────────────────┐   │
│  │ Terms of Service      > │   │
│  ├─────────────────────────┤   │
│  │ Privacy Policy        > │   │
│  ├─────────────────────────┤   │
│  │ OSS Licenses          > │   │
│  └─────────────────────────┘   │
│                                 │
│  ACCOUNT                        │
│  ┌─────────────────────────┐   │
│  │ 🚪 Sign Out             │   │
│  └─────────────────────────┘   │
│                                 │
├─────────────────────────────────┤
│  [🏠] [🔍] [🎸] [⚙️]           │
└─────────────────────────────────┘
```

## My Area Bottom Sheet

```
┌─────────────────────────────────┐
│  Change My Area                 │
│                                 │
│  Step 1: Select Region          │
│  ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ 北海道 │ │ 東北  │ │ 関東  │   │
│  └──────┘ └──────┘ └──────┘   │
│  ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ 中部  │ │ 近畿  │ │ 中国  │   │
│  └──────┘ └──────┘ └──────┘   │
│  ┌──────┐ ┌──────┐            │
│  │ 四国  │ │ 九州  │            │
│  └──────┘ └──────┘            │
│                                 │
│  Step 2: Select Prefecture      │
│  (filtered by selected region)  │
│                                 │
└─────────────────────────────────┘
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Layout style | Grouped list (iOS-style) | Clean, familiar settings pattern for mobile |
| My Area UI | Bottom sheet with 2-step selection | Reuses onboarding mental model |
| Sign Out position | Bottom of page, red text | Convention for destructive actions |
| Legal pages | External links (static pages) | No in-app rendering needed for MVP |
| Area persistence | Frontend state (localStorage) for MVP | Backend preference API deferred to post-MVP |

## Risks

- **Area change without backend sync**: For MVP, area preference is stored locally. If user switches devices, area resets. Acceptable for MVP.
