# Tasks: Passion Level

## Tasks

### Backend
- [ ] Add `passion_level` column to `followed_artists` table (DB migration)
- [ ] Define `PassionLevel` enum in protobuf schema
- [ ] Implement `SetPassionLevel` RPC in ArtistService
- [ ] Extend `ListFollowed` response to include passion level per artist
- [ ] Add repository layer support for passion level CRUD

### Frontend — My Artists
- [ ] Add passion level indicator (🔥🔥/🔥/👀) to each artist row
- [ ] Create passion level selector dropdown/bottom sheet
- [ ] Integrate SetPassionLevel RPC on selection change (optimistic update)

### Frontend — Dashboard Mutation UI
- [ ] Add logic to detect Must Go artists in Lane 2/3 event data
- [ ] Create MutationCard component (expanded size, vivid color, badge)
- [ ] Integrate Mutation cards into Lane 2 and Lane 3 rendering
- [ ] Ensure layout handles multiple mutated cards on the same date without overflow
