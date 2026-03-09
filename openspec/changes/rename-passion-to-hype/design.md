## Context

The current PassionLevel system (3 tiers: MUST_GO, LOCAL_ONLY, KEEP_AN_EYE) was implemented as a UI-only feature — the notification backend sends push notifications to all followers regardless of their passion level. This change renames the concept to "Hype", expands to 4 tiers with clear notification semantics, and implements the actual notification filtering logic.

Current state:
- Proto: `PassionLevel` enum in `entity/v1/artist.proto` with values 1-3
- DB: `followed_artists.passion_level TEXT DEFAULT 'local_only'`
- Backend: `NotifyNewConcerts()` sends to ALL followers, ignoring passion level
- Frontend: Passion selector with 3 options on My Artists page

## Goals / Non-Goals

**Goals:**
- Rename PassionLevel → HypeType (proto) / Hype (all other layers) with clear ascending semantics
- Implement notification filtering: WATCH=off, HOME=home-area-only, ANYWHERE=all
- Change default to ANYWHERE so new followers immediately receive notifications
- Define NEARBY in proto for forward compatibility (Phase 2)

**Non-Goals:**
- NEARBY tier implementation (requires physical distance calculation — undefined)
- NEARBY UI exposure (hidden from selector in Phase 1)
- Dashboard Visual Mutation (large cards in Lane 2/3 for ANYWHERE artists)
- Notification history or delivery tracking

## Decisions

### Decision 1: Naming convention — HypeType (proto) vs Hype (everywhere else)

Proto enum follows Protobuf convention as a suffixed type name: `HypeType`. All other layers use the shorter domain term: `Hype`.

| Layer | Name |
|-------|------|
| Proto enum | `HypeType` |
| Proto field | `hype` (in `FollowedArtist` message) |
| RPC | `SetHype` |
| DB column | `hype` |
| Go entity | `Hype` (type), `HypeWatch`, `HypeHome`, etc. (constants) |
| Frontend | `hype` property, `hypeIcon()`, `HYPE_META` |
| i18n key | `hype.watch`, `hype.home`, `hype.nearby`, `hype.anywhere` |

**Rationale**: "Hype" is shorter, more evocative, and aligns with music culture. The `Type` suffix is only needed in proto where bare `Hype` would not follow enum naming conventions.

### Decision 2: Enum value numbering — ascending hype order

```protobuf
enum HypeType {
  HYPE_TYPE_UNSPECIFIED = 0;
  HYPE_TYPE_WATCH    = 1;  // 👀 lowest hype
  HYPE_TYPE_HOME     = 2;  // 🔥
  HYPE_TYPE_NEARBY   = 3;  // 🔥🔥 (Phase 2)
  HYPE_TYPE_ANYWHERE = 4;  // 🔥🔥🔥 highest hype
}
```

**Rationale**: Ascending order enables natural comparisons (`hype >= HOME` means "at least home-level notifications"). The current PassionLevel uses descending order (MUST_GO=1 is highest) which is counterintuitive.

**Alternative considered**: Keep descending order for backward compatibility. Rejected because this is a full rename anyway — a clean break is better than carrying over a confusing convention.

### Decision 3: Notification filtering in NotifyNewConcerts

The filtering logic is added to `NotifyNewConcerts()` in the push notification use case. The method must now:

1. Retrieve followers WITH their hype level (new: `ListFollowersWithHype`)
2. For each follower, evaluate whether to send based on hype:
   - `WATCH` → skip
   - `HOME` → send only if `concert.venue.adminArea == user.home.level_1`
   - `NEARBY` → treat as ANYWHERE (Phase 1 fallback, not selectable in UI)
   - `ANYWHERE` → send

This requires a new repository method that joins `followed_artists` with `users` and `homes` to get hype + home area in one query.

**Alternative considered**: Filter at the query level (only fetch followers who should be notified). Rejected for Phase 1 because the logic is simple enough in-memory and keeping the query simple makes it easier to extend for NEARBY later.

### Decision 4: DB migration strategy — rename column in-place

Single migration that:
1. Renames column `passion_level` → `hype`
2. Updates existing values: `must_go` → `anywhere`, `local_only` → `anywhere`, `keep_an_eye` → `watch`
3. Drops old CHECK constraint, adds new one: `('watch', 'home', 'nearby', 'anywhere')`
4. Changes DEFAULT to `'anywhere'`

**Value mapping rationale**:
- `must_go` → `anywhere`: Same intent (travel anywhere)
- `local_only` → `anywhere`: Users who were on the old default should be bumped to the new default so they start receiving notifications. This aligns with the product goal of "experience notifications first".
- `keep_an_eye` → `watch`: Same intent (no notifications)

**Alternative considered**: Map `local_only` → `home`. Rejected because `local_only` users never actually received filtered notifications (the feature wasn't implemented), so they had no expectation of "home only" behavior. Mapping to `anywhere` gives them the intended new-user experience.

### Decision 5: NEARBY in Phase 1 — proto-defined but UI-hidden

NEARBY is included in the proto enum (value=3) and DB CHECK constraint but:
- Frontend hype selector does NOT show NEARBY as an option
- Backend treats NEARBY as ANYWHERE (fallback) if somehow set
- No region/distance calculation is implemented

**Rationale**: Including NEARBY in proto now avoids a breaking proto change in Phase 2. The enum is additive-safe but renumbering is not.

### Decision 6: Default on follow — ANYWHERE

When a user follows an artist, `hype` defaults to `'anywhere'` (DB DEFAULT). This means new followers immediately receive push notifications for all concerts.

**Rationale**: The product goal is to let users experience notifications before deciding to tune them down. The selector UI makes it easy to change.

## Risks / Trade-offs

**[Risk] Notification volume spike** → Users who follow many artists will receive many notifications with the new ANYWHERE default. Mitigated by: (1) the hype selector is prominent and easy to use, (2) notifications are already batched per artist per discovery run, (3) users can unsubscribe from push entirely.

**[Risk] Breaking proto change across repos** → Enum rename + value remapping requires coordinated release. Mitigated by: standard specification-first release process (spec PR → merge → Release → BSR gen → backend/frontend update).

**[Risk] Data migration maps local_only → anywhere** → Existing `local_only` users may receive more notifications than before. Mitigated by: they weren't receiving any filtered notifications anyway (feature was unimplemented), so this is net-new behavior regardless.

**[Trade-off] NEARBY fallback to ANYWHERE** → If a user somehow has NEARBY set (e.g., via direct DB edit), they get all notifications instead of filtered ones. Acceptable for Phase 1 since NEARBY is not exposed in UI.

## Migration Plan

1. **specification**: Create PR with proto changes (enum rename, field rename, RPC rename). Merge → Release → BSR publishes new types.
2. **backend**: DB migration (column rename + value mapping + constraint + default). Update entity, repository, use case, handler, mapper. Add `ListFollowersWithHype` query. Update `NotifyNewConcerts` with filtering logic.
3. **frontend**: Update service clients, My Artists component, i18n, onboarding to use new naming and 4-tier selector (NEARBY hidden).

Rollback: Proto changes are breaking and not easily rolled back. DB migration can be reversed with an inverse migration. Backend/frontend changes are straightforward reverts.
