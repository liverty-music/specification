## Context

To improve the quality of the onboarding experience, we will introduce an interactive flow where "recommended" artists are automatically extracted from the user's YouTube watch history, allowing them to follow related artists from there. This is a wide-ranging change across `specification` (API definition), `backend` (OAuth2/AI analysis), and `frontend` (UX/UI).

## Goals / Non-Goals

**Goals:**
- Build a high-precision artist inference pipeline combining YouTube Data API and Gemini API.
- Ensure reliable linking from inferred artist names to external metadata (MBID/Last.fm).
- Provide a loading UX that makes users feel "the AI understands my preferences."

**Non-Goals:**
- Support for data sources other than YouTube (e.g., Spotify).
- Permanent storage of the user's entire watch history (extract and use only necessary artist names, discard raw data).

## Decisions

### 1. Server-side Inference Pipeline
**Decision**: Receive the OAuth2 token from the client, retrieve subscription/liked info from YouTube Data API on the backend, and extract artist names using a fast LLM such as Gemini 1.5 Flash.
**Rationale**: Avoid management of sensitive information on the client side and allow for prompt control and result normalization (deduplication) on the backend.

### 2. Data Source Priority
**Decision**: Identify and present artists to the user in the following order:
1. **YouTube Subscriptions**: Extraction from channel names (high precision).
2. **YouTube Liked Videos**: Extraction from video titles (more noise, but high volume).
3. **Geo Top Results (Last.fm)**: Fallback if identification fails.

### 3. API Design: ArtistService
**Decision**: Consolidate onboarding-specific recommendations in addition to artist information management (Search, Follow).
- `GetOnboardingSuggestions`: Returns YouTube integration results.
- `ListSimilarArtists`: Chain-like recommendations starting from a follow action.

## Risks / Trade-offs

- **[Risk] YouTube API Quota Limits** → Avoid `search` endpoint and limit to `list` (subscriptions, liked videos) to reduce costs.
- **[Trade-off] Gemini Inference Speed** → To avoid making the user wait, notify the frontend of analysis progress in detail (e.g., "Step 1/3: Communicating with YouTube...").
- **[Risk] Mistaken Identity (Same-named Artists)** → Consider not only string matching but also similarity and reputation in the existing database to select the most certain MBID.
