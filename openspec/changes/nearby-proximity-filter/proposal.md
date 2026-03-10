## Why

The `rename-passion-to-hype` change introduces `HYPE_TYPE_NEARBY` in the proto enum but leaves it unimplemented — the UI hides it and the backend falls back to ANYWHERE behavior. To complete the 4-tier hype system, the NEARBY tier needs a concrete proximity definition that determines which concerts are "close enough" to notify users about. Unlike HOME (exact ISO 3166-2 match), NEARBY requires physical distance calculation between the user's home area and a concert venue's area, which is a fundamentally different kind of geographic filtering that does not yet exist in the system.

## What Changes

- Define a proximity model for NEARBY: given a user's home area (ISO 3166-2 code) and a concert venue's admin area (ISO 3166-2 code), determine whether the venue is "nearby"
- Choose a distance strategy — options include:
  - **Centroid distance**: Calculate distance between geographic centroids of the two admin areas, with a configurable radius threshold
  - **Adjacency graph**: Precompute a neighbor list for each admin area (e.g., Tokyo is adjacent to Saitama, Chiba, Kanagawa) and define "nearby" as N-hop adjacency
  - **Region grouping**: Use predefined region groups (Kanto, Kansai, etc.) — simpler but less accurate and conflates UI grouping with business logic
- Implement the chosen model in the backend notification filter so `HYPE_TYPE_NEARBY` sends notifications for concerts in the user's home area AND nearby areas
- Expose NEARBY as a selectable option in the frontend hype selector (currently hidden)
- Update the Dashboard Live Highway lane assignment if needed (NEARBY notifications should correspond to Lane 1 + Lane 2 concerts)

## Capabilities

### New Capabilities

- `nearby-proximity`: Definition of geographic proximity between ISO 3166-2 admin areas, including the distance/adjacency model, data source, and query interface used by the notification filter

### Modified Capabilities

- `hype-notification-filter`: NEARBY tier transitions from ANYWHERE fallback to actual proximity-based filtering using the new proximity model
- `my-artists`: Hype selector exposes NEARBY (🔥🔥) as a fourth selectable option between HOME and ANYWHERE

## Impact

- **backend**: New proximity data source (static lookup table or geospatial query), updated notification filter logic in `NotifyNewConcerts()`, possible new DB table or config for area proximity data
- **frontend**: Hype selector updated to show 4 options instead of 3
- **specification**: No proto changes needed (NEARBY already defined in HypeType enum)
- **data**: Requires geographic centroid or adjacency data for all 47 Japanese prefectures (Phase 1); extensible to other countries via ISO 3166-2
