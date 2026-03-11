## REMOVED Requirements

### Requirement: Handle artists without MBID

**Reason**: Artists without MBID cannot be deduplicated and produce orphaned rows that are never surfaced to users. All use-case flows (Search, ListSimilar, ListTop) already filter out MBID-less artists via `FilterArtistsByMBID()` before persisting. The no-MBID INSERT path in the repository is dead code. The `artists.mbid` column will be made NOT NULL, and the 1697 existing orphaned rows (dev DB) will be deleted.

**Migration**: The repository's no-MBID bulk INSERT query (`insertArtistsNoMBIDUnnestQuery`) and its branching logic SHALL be removed. Artists returned by external APIs without an MBID SHALL be silently excluded from persistence (existing behavior via `FilterArtistsByMBID()`). No API-level changes are required.
