# Proposal: Discover Page

## Problem

After onboarding, users have no way to discover and follow new artists. The Bubble UI experience from onboarding is a one-time interaction. Users who want to explore new genres, find specific artists, or simply browse for inspiration have no dedicated space to do so.

## Solution

Implement the **Discover page** (Tab 2) with two modes:

1. **Bubble UI (Re-experience)** — Reuse the onboarding DNA Orb Bubble UI in a fullscreen mode with genre/tag switching chips at the top. Users can re-experience the gamified discovery anytime.
2. **Manual Search** — A text search bar (using existing artist search capabilities) for targeted artist lookup. Results displayed as a simple list with tap-to-follow using the same DNA Orb absorption effect.

## Scope

### In Scope

- Discover page with Bubble UI re-experience mode
- Genre/tag chips for filtering bubble content (Rock, Pop, Anime, etc.)
- Manual text search bar
- Search results as a list with follow action
- Integration with existing ArtistService RPCs (ListTop, ListSimilar, Follow)

### Out of Scope

- New backend search API (reuses existing `artist.search` via Last.fm)
- Recommendation algorithm changes
- Social discovery (friend-based recommendations)

## Impact

- New spec: `discover`
- Reuses: `artist-discovery-dna-orb-ui` spec (Bubble UI components)

## Dependencies

- `bottom-navigation-shell` (route `/discover` and tab must exist)

## Blocked By

- `bottom-navigation-shell`
