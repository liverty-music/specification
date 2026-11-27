## REMOVED Requirements

### Requirement: Centroid of a supported level 1 area

**Reason**: The point NEARBY is measured from is the reference point of an Area, which Area.Resolve returns for any first-level code; a lookup on the User entity, limited to the 47 Japanese prefectures, is no longer needed.
**Migration**: Callers resolve the level 1 code with Area.Resolve and read the Area's reference point (ConcertUseCase.ListByArtists "The home's reference point is its Area's"); a stored Home already has its Area's reference point (User entity "A Home's reference point is its Area's").
