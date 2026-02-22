# Design: Passion Level

## Data Model

```
followed_artists table (existing)
  + passion_level: TEXT  (default: 'local_only')
    enum values: 'must_go', 'local_only', 'keep_an_eye'
```

```protobuf
// Package: liverty_music.entity.v1
// PassionLevel is defined in the entity package alongside Artist,
// and referenced as entity.v1.PassionLevel in RPC definitions.

// PassionLevel represents the user's enthusiasm tier for a followed artist.
// It determines dashboard visibility and notification behavior.
enum PassionLevel {
  PASSION_LEVEL_UNSPECIFIED = 0;
  PASSION_LEVEL_MUST_GO = 1;      // 🔥🔥 Travel anywhere
  PASSION_LEVEL_LOCAL_ONLY = 2;    // 🔥 Default
  PASSION_LEVEL_KEEP_AN_EYE = 3;  // 👀 No push notifications
}
```

## My Artists Page — Passion Selector

```
┌─────────────────────────────────┐
│  🎸 My Artists          (12)    │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │ ■ RADWIMPS      [🔥🔥 ▼]│   │  ← tappable selector
│  ├─────────────────────────┤   │
│  │ ■ ONE OK ROCK   [🔥  ▼] │   │
│  ├─────────────────────────┤   │
│  │ ■ Aimer         [👀  ▼] │   │
│  └─────────────────────────┘   │
│                                 │
│  Selector dropdown:             │
│  ┌─────────────────┐           │
│  │ 🔥🔥 Must Go     │           │
│  │ 🔥  Local Only   │           │
│  │ 👀  Keep an Eye  │           │
│  └─────────────────┘           │
└─────────────────────────────────┘
```

## Dashboard — Visual Mutation UI

When a Must Go (🔥🔥) artist's event appears in Lane 2 or Lane 3:

```
Normal Lane 2/3 card:        Mutated card (Must Go):
┌──────────┐                 ┌──────────────────┐
│ Artist   │                 │ 🔥 遠征チャンス    │  ← badge
│ 福岡     │                 │                    │
└──────────┘                 │  RADWIMPS          │  ← mega typography
                             │  福岡              │
                             │                    │
                             └──────────────────────┘
                               ↑ expanded size
                               ↑ vivid accent color / stripe pattern
```

### Mutation Rules

| Condition | Lane 1 | Lane 2 | Lane 3 |
|-----------|--------|--------|--------|
| Must Go 🔥🔥 | Normal (already prominent) | **MUTATE** — expand + badge | **MUTATE** — expand + badge |
| Local Only 🔥 | Normal | Normal | Normal (compact) |
| Keep an Eye 👀 | Normal | Normal | Normal (compact) |

## API Design

```protobuf
// SetPassionLevel updates the user's preference for an artist's notification tier.
rpc SetPassionLevel(SetPassionLevelRequest) returns (SetPassionLevelResponse);

// SetPassionLevelRequest provides the artist ID and the new passion level to be set.
message SetPassionLevelRequest {
  // Required. The unique identifier of the artist.
  entity.v1.ArtistId artist_id = 1 [(buf.validate.field).required = true];

  // Required. The new passion level tier.
  entity.v1.PassionLevel passion_level = 2 [
    (buf.validate.field).required = true,
    (buf.validate.field).enum.defined_only = true
  ];
}

// SetPassionLevelResponse is returned upon a successful update.
message SetPassionLevelResponse {}
```

The passion level is returned as part of the followed artist data in `ListFollowed`. The `FollowedArtist` response message is extended as follows:

```protobuf
message FollowedArtist {
  // ... existing fields ...

  // The user's passion level for this artist.
  entity.v1.PassionLevel passion_level = 4;
}
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default level | Local Only (🔥) | Non-intrusive default; user opts in to more notifications |
| Persistence | Backend (DB column) | Syncs across devices, used by notification system |
| Mutation scope | Lane 2 + Lane 3 only | Lane 1 cards are already prominent |
| Selector UI | Inline dropdown per row | Quick toggle without leaving the list |

## Risks

- **Dashboard complexity**: Mutation UI adds conditional rendering logic to an already complex 3-lane layout. Needs careful CSS to avoid breaking lane alignment.
- **Backend migration**: Adding `passion_level` column to `followed_artists` requires a database migration.
