# Design: My Artists List

## UI Structure

```
┌─────────────────────────────────┐
│  🎸 My Artists          (12)    │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │ ■ RADWIMPS              │   │  ← color accent from name
│  ├─────────────────────────┤   │
│  │ ■ ONE OK ROCK           │   │
│  ├─────────────────────────┤   │
│  │ ■ Aimer                 │   │
│  ├─────────────────────────┤   │
│  │ ■ King Gnu              │   │
│  ├─────────────────────────┤   │
│  │ ■ YOASOBI               │   │
│  └─────────────────────────┘   │
│         ...                     │
│                                 │
├─────────────────────────────────┤
│  [🏠] [🔍] [🎸] [⚙️]           │
└─────────────────────────────────┘
```

## Swipe-to-Unfollow

```
Normal state:
┌─────────────────────────────┐
│ ■ RADWIMPS                  │
└─────────────────────────────┘

Swiped left:
┌──────────────────────┐┌─────┐
│ ■ RADWIMPS           ││ ✕   │  ← red delete zone
└──────────────────────┘└─────┘

After unfollow (bottom toast):
┌─────────────────────────────┐
│ "RADWIMPS unfollowed"  [Undo]│
└─────────────────────────────┘
  ↑ auto-dismiss after 5 seconds
```

## Data Flow

```
MyArtistsPage
  │
  ├── on mount → ArtistService.ListFollowed() → populate list
  │
  └── on swipe/unfollow
        ├── remove from local list immediately (optimistic)
        ├── show Undo toast (5 sec timer)
        │     ├── if Undo tapped → re-add to list, cancel RPC
        │     └── if timer expires → ArtistService.Unfollow(artistId)
        └── done
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| View mode | List only (no grid/festival) | MVP simplicity; grid view is post-MVP |
| Unfollow UX | Swipe + Undo toast | Frictionless, no confirmation dialog (per UX spec) |
| Unfollow timing | Delayed RPC (after undo window) | Allows recovery without extra API calls |
| Color accent | Reuse Dashboard's deterministic HSL algorithm | Visual consistency across app |
| Empty state | Friendly message + link to Discover tab | Guide users to follow artists |

## Risks

- **Swipe gesture conflicts**: Bottom sheet or other swipeable elements on the page could conflict. Since this page has no bottom sheets, risk is low.
- **Long lists**: If a user follows hundreds of artists, virtualized list rendering may be needed. For MVP with typical follow counts (10-50), standard rendering suffices.
