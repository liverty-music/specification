## REMOVED Requirements

### Requirement: Passion Level Tiers

**Reason**: Replaced by HypeType system with 4 tiers (WATCH, HOME, NEARBY, ANYWHERE) instead of 3 tiers (Must Go, Local Only, Keep an Eye). See new capability `hype-notification-filter` and modified capabilities `artist-following`, `my-artists`.

**Migration**: All references to PassionLevel, passion_level, passion-level are renamed to HypeType (proto) / Hype (elsewhere). Tier mapping: must_go → anywhere, local_only → anywhere, keep_an_eye → watch.

### Requirement: Passion Level Persistence

**Reason**: Replaced by Hype persistence with identical cross-device sync behavior but different column name and values.

**Migration**: DB column `passion_level` renamed to `hype`. Values migrate per tier mapping above.

### Requirement: SetPassionLevel API

**Reason**: Replaced by `SetHype` RPC with the same semantics but accepting HypeType enum values.

**Migration**: RPC renamed from `SetPassionLevel` to `SetHype`. Request message renamed from `SetPassionLevelRequest` to `SetHypeRequest`.

### Requirement: PassionLevel in ListFollowed Response

**Reason**: Replaced by `hype` field in `FollowedArtist` message using `HypeType` enum.

**Migration**: `FollowedArtist.passion_level` field renamed to `FollowedArtist.hype` with type `HypeType`.
