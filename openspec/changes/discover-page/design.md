# Design: Discover Page

## UI Structure

```
┌─────────────────────────────────┐
│  🔍 Discover                    │
├─────────────────────────────────┤
│  [🔎 Search artists...       ] │  ← search bar
│                                 │
│  [Rock] [Pop] [Anime] [Jazz]   │  ← genre chips
│  [Electronic] [Hip-Hop] ...    │
│                                 │
│      ┌───┐                     │
│    ┌───┐ ┌───┐                 │
│  ┌───┐     ┌───┐ ┌───┐        │
│    ┌───┐ ┌───┐   ┌───┐        │  ← floating bubbles
│  ┌───┐     ┌───┐               │
│      ┌───┐   ┌───┐             │
│                                 │
│         ┌──────────┐           │
│         │ Music DNA│           │  ← DNA Orb
│         │  (orb)   │           │
│         └──────────┘           │
│                                 │
├─────────────────────────────────┤
│  [🏠] [🔍] [🎸] [⚙️]           │
└─────────────────────────────────┘
```

## Search Mode

```
┌─────────────────────────────────┐
│  🔍 Discover                    │
├─────────────────────────────────┤
│  [🔎 "BUMP OF CHICKEN"    ✕  ] │  ← active search
│                                 │
│  Search Results:                │
│  ┌─────────────────────────┐   │
│  │ ■ BUMP OF CHICKEN  [+]  │   │  ← tap to follow
│  ├─────────────────────────┤   │
│  │ ■ BUMP (similar)    [+]  │   │
│  └─────────────────────────┘   │
│                                 │
│  Tap [+] triggers DNA Orb      │
│  absorption animation           │
│                                 │
├─────────────────────────────────┤
│  [🏠] [🔍] [🎸] [⚙️]           │
└─────────────────────────────────┘
```

## Mode Switching

```
Default state: Bubble UI mode (fullscreen bubbles + genre chips)
                    │
         User taps search bar
                    │
                    ▼
Search mode: Keyboard up, list results, bubbles hidden
                    │
         User clears search / taps ✕
                    │
                    ▼
Back to Bubble UI mode
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default mode | Bubble UI (not search) | Discovery is exploratory; search is targeted |
| Bubble UI source | Reuse onboarding ArtistDiscovery component | DRY; same physics engine, animations, and orb |
| Genre chips | Top-level filter, regenerates bubbles | Quick mood-based exploration |
| Search results | Simple list (not bubbles) | Per UX spec; search is utilitarian |
| Follow from search | Same DNA Orb absorption effect | Consistent follow UX across app |
| Already-followed indicator | Dimmed or checkmark on bubble/row | Prevent confusion on re-follow |

## Component Reuse

The key insight is reusing the `ArtistDiscovery` component from onboarding:

```
Onboarding flow          Discover tab
     │                        │
     └── ArtistDiscovery ─────┘  (shared component)
              │
         Differences:
         - Onboarding: auto-load top artists, has "View Schedule" CTA
         - Discover: genre chips filter, no completion CTA, search bar overlay
```

## Risks

- **Component adaptation**: The onboarding ArtistDiscovery component was built for a one-time flow. Extracting it for reuse may require refactoring its lifecycle and state management.
- **Performance**: Running physics-based bubbles on a tab that users might switch to frequently. Need to pause/resume physics when tab is not active.
