## Context

The `SearchNewConcerts` usecase is currently internal to the backend. We need to expose it via the `ConcertService` RPC interface to allow clients to trigger on-demand concert discovery.

## Goals / Non-Goals

**Goals:**

- Expose `SearchNewConcerts` via Connect-RPC.
- Define type-safe request and response messages.
- Ensure proper validation and error handling.

**Non-Goals:**

- Changes to the underlying search logic (Gemini/Scraper).
- Changes to the persistence logic.

## Decisions

### Decision: RPC Naming and Signature

We will use the name `SearchNewConcerts` for the RPC method, consistent with the usecase.
**Request**: `SearchNewConcertsRequest`
**Response**: `SearchNewConcertsResponse`
**Rationale**: Adheres to Google AIP and Connect-Go conventions.

### Decision: Request Parameters

The request will include `artist_id` as a required field.
**Rationale**: The search is artist-centric.

### Decision: Error Mapping

We will map backend `apperr` codes to standard Connect/gRPC error codes.

- `codes.InvalidArgument` -> `connect.CodeInvalidArgument`
- `codes.NotFound` -> `connect.CodeNotFound`
- Default -> `connect.CodeInternal`

## Risks / Trade-offs

- [Risk] Performance: Search might be slow due to external API calls. → Mitigation: Ensure the client handles timeouts appropriately; search is already optimized in the usecase.
