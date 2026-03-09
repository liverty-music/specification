## Why

The current PassionLevel system has two problems: (1) it defines three tiers but the notification backend ignores them entirely — all followers receive all push notifications regardless of their passion level, and (2) the naming ("Passion Level", "Local Only", "Must Go") does not clearly communicate the relationship between user enthusiasm and notification scope. Renaming to "Hype" with semantically clear tier names (Watch, Home, Nearby, Anywhere) establishes a direct mapping between the user's intent and the system's notification behavior, while also preparing for a future Nearby tier based on physical distance.

## What Changes

- **BREAKING**: Rename `PassionLevel` enum to `HypeType` in proto; rename to `Hype` in all other layers (DB column, Go entity, frontend)
- **BREAKING**: Expand from 3 tiers to 4 tiers with ascending hype order:
  - `WATCH` (👀) — Dashboard only, no push notifications
  - `HOME` (🔥) — Push notifications only for concerts in user's home area (ISO 3166-2 match)
  - `NEARBY` (🔥🔥) — Reserved for Phase 2 (physical distance based); defined in proto but hidden from UI
  - `ANYWHERE` (🔥🔥🔥) — Push notifications for all concerts nationwide
- **BREAKING**: Change default on follow from `LOCAL_ONLY` to `ANYWHERE` so users immediately experience notifications
- **BREAKING**: Rename `SetPassionLevel` RPC to `SetHype`; rename `FollowedArtist.passion_level` field to `hype`
- Implement notification filtering in `NotifyNewConcerts()` based on hype and user home area
- DB migration: rename column `passion_level` to `hype`, update CHECK constraint and default value

## Capabilities

### New Capabilities

- `hype-notification-filter`: Notification filtering logic that evaluates a follower's hype and home area against a concert's venue location to determine whether to send a push notification

### Modified Capabilities

- `passion-level`: Replaced entirely by the new hype system — tiers, naming, enum values, default, and API all change
- `artist-following`: FollowedArtist wrapper field renamed from `passion_level` to `hype`; default value changes to `anywhere`
- `my-artists`: Passion selector UI renamed to Hype selector; icons and labels updated; NEARBY tier hidden in Phase 1
- `push-notification`: NotifyNewConcerts must filter recipients by hype (WATCH excluded, HOME filtered by venue location)

## Impact

- **specification**: Proto enum rename + restructure, RPC rename, field renames across entity and RPC layers
- **backend**: Entity types, use case logic, RPC handler/mapper, repository queries, DB migration (column rename + constraint + default)
- **frontend**: Service clients, My Artists page component/template, i18n keys (EN/JA), onboarding step 5, passion explanation dialog
- **Cross-repo coordination**: Specification PR must merge and release first; backend and frontend PRs depend on BSR-generated types
