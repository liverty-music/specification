## 1. API Definitions (Protobuf)

- [ ] 1.1 New definitions for `ArtistService`: `SearchArtists`, `FollowArtist`, `ListSimilarArtists`, etc.
- [ ] 1.2 Definition of `GetOnboardingSuggestions` messages and RPC.
- [ ] 1.3 Cleanup of existing `Artist` message and addition of MBID validation.
- [ ] 1.4 Pass compatibility checks with `buf lint` and `buf breaking`.

## 2. Backend Implementation (Core Logic)

- [ ] 2.1 Implementation of YouTube Data API client (Subscriptions/Liked Videos retrieval).
- [ ] 2.2 Gemini API prompt engineering: Noise removal and artist extraction.
- [ ] 2.3 Artist normalization logic: Extracted name -> MBID resolution.
- [ ] 2.4 Implementation of similar artist retrieval via Last.fm API.
- [ ] 2.5 Persisting user follow state (including DB schema changes).

## 3. Frontend Implementation (UX/UI)

- [ ] 3.1 Implementation of Google Login and YouTube scope request.
- [ ] 3.2 Onboarding loading animation: Visualization of analysis progress.
- [ ] 3.3 Interactive follow UI: Chain-like suggestions and drill-down.
- [ ] 3.4 Redirect logic to dashboard after initial follow completion.

## 4. Verification & Sync

- [ ] 4.1 End-to-end testing in development environment (YouTube Login -> Follow -> Live Info display).
- [ ] 4.2 Sync delta specs across repositories (`/opsx-sync`).
