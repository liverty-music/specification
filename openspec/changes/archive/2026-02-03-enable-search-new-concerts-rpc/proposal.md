## Why

Currently, the `SearchNewConcerts` capability exists only at the usecase layer in the backend. To enable frontend applications or other services to trigger concert discovery for an artist, this capability must be exposed via an RPC interface.

## What Changes

- **Add RPC Method**: Introduce `SearchNewConcerts` to `ConcertService` in the Protobuf definition.
- **Implement Handler**: Implement the `SearchNewConcerts` RPC handler in the backend to delegate to the existing `ConcertUseCase`.
- **Validation**: Ensure `artist_id` is validated as a required field in the RPC request.

## Capabilities

### New Capabilities

- `concert-search`: Define the RPC interface and behavior for searching new concerts for an artist.

### Modified Capabilities

- `live-events`: Requirements change to include triggering discovery via an API.

## Impact

- **Specification**: `concert_service.proto` will be modified.
- **Backend**: `concert_service.go` (or equivalent handler) will be updated to implement the new RPC.
- **API**: New RPC endpoint `liverty_music.rpc.v1.ConcertService/SearchNewConcerts` will be available.
