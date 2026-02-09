## Why

When users start using the service, we want to eliminate the effort of manually searching for and registering artists. By automatically inferring and suggesting favorite artists from YouTube watch history, we can provide personalized concert information from the very beginning. Additionally, we provide a "chain-following" experience where users can discover and follow related artists, enhancing the onboarding satisfaction.

## What Changes

- **YouTube Data API Integration**: Retrieve user's subscribed channels and liked videos during Google Sign-in to identify favorite artists.
- **Artist Inference via Gemini**: Filter YouTube noise (non-music videos) using Gemini to extract clean artist names.
- **Live Info Complementation via Gemini Search**: Use Gemini (Grounding with Google Search) to identify the latest tour information for artists not present in the local database.
- **New ArtistService**: Provide RPCs for artist search, follow, retrieving similar artists, and getting recommendations for onboarding.
- **Aurelia 2 Onboarding UI**: Implement a UI that visualizes the YouTube data analysis progress and allows users to interactively follow inferred artists.

## Capabilities

### New Capabilities
- `artist-onboarding`: Provides artist inference from YouTube history and an interactive initial follow flow.
- `artist-discovery`: Utilizes Last.fm API and Gemini Search to provide live information for artists unknown to the user or missing from the database.

### Modified Capabilities
- `intel`: Adds logic for deduplicating YouTube data and extracting (inferring) live information from unstructured web data.

## Impact

- **API**: New `ArtistService`. Cleanup of existing definitions such as `FollowRequest` (**BREAKING**).
- **Infrastructure**: New dependencies on YouTube Data API (addition of OAuth 2.0 Scope) and Gemini API (Vertex AI).
- **Frontend**: Implementation of a dedicated onboarding view using Aurelia 2.
- **Identity**: Request `youtube.readonly` scope during Google integration in Zitadel.
