# Tasks: Passion Level

## Tasks

### Protobuf Schema
- [ ] Define `PassionLevel` enum in `entity/v1/entity.proto`
- [ ] Add `FollowedArtist` wrapper message in `rpc/artist/v1/artist_service.proto`
- [ ] Define `SetPassionLevelRequest` / `SetPassionLevelResponse` messages
- [ ] Add `SetPassionLevel` RPC to `ArtistService`
- [ ] Update `ListFollowedResponse` to use `repeated FollowedArtist` instead of `repeated Artist`

### Backend
- [ ] Add `passion_level` column to `followed_artists` table (Atlas migration)
- [ ] Add `PassionLevel` type to entity layer (`internal/entity/artist.go`)
- [ ] Add `SetPassionLevel` method to `ArtistRepository` interface
- [ ] Implement `SetPassionLevel` in PostgreSQL repository (`artist_repo.go`)
- [ ] Update `ListFollowed` query to return `passion_level` column
- [ ] Add `SetPassionLevel` method to `ArtistUseCase` interface and implementation
- [ ] Add `SetPassionLevel` handler to `ArtistHandler` (RPC layer)
- [ ] Add `FollowedArtistToProto` mapper function
- [ ] Update `ListFollowed` handler to return `FollowedArtist` wrapper

### Frontend — My Artists
- [ ] Update `FollowedArtist` interface to include `passionLevel` field
- [ ] Update `ListFollowed` consumer to handle `FollowedArtist` wrapper response
- [ ] Add passion level indicator (🔥🔥/🔥/👀) to each artist row
- [ ] Create passion level selector dropdown/bottom sheet
- [ ] Integrate `SetPassionLevel` RPC on selection change (optimistic update)

### Frontend — My Artists Grid (Festival) View
- [ ] Add view toggle control (List / Grid) to the My Artists page header
- [ ] Create Grid (Festival) View component with poster-style tiles
- [ ] Size tiles based on passion level (Must Go tiles are larger)
- [ ] Implement long-press context menu for passion level and unfollow in Grid View

### Frontend — Dashboard Mutation UI
- [ ] Add logic to detect Must Go artists in Lane 2/3 event data
- [ ] Create MutationCard component (expanded size, vivid color, badge)
- [ ] Integrate Mutation cards into Lane 2 and Lane 3 rendering
- [ ] Ensure layout handles multiple mutated cards on the same date without overflow
