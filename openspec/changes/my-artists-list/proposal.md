# Proposal: My Artists List

## Problem

After onboarding, users have no way to view or manage their followed artists. The only interaction point is the Bubble UI during onboarding. Users need to see who they follow and be able to unfollow artists they are no longer interested in.

## Solution

Implement the **My Artists page** (Tab 3) with a list view showing all followed artists and swipe-to-unfollow functionality. The unfollow action uses a frictionless Undo toast pattern instead of a confirmation dialog.

## Scope

### In Scope

- My Artists page with vertical list of followed artists
- Each row: artist name (+ optional dynamically generated color accent)
- Unfollow via swipe-left gesture or long-press
- Undo toast (no confirmation dialog) for accidental unfollow recovery
- Call existing `ArtistService.Unfollow` RPC
- Call existing `ArtistService.ListFollowed` RPC to populate the list

### Out of Scope

- Passion Level (heat/enthusiasm) selector per artist (separate change: `passion-level`)
- Grid/Festival view toggle (post-MVP)
- Artist detail page
- Any new backend API (uses existing RPCs)

## Impact

- New spec: `my-artists`
- Uses existing: `artist-following` spec (ListFollowed, Unfollow RPCs)

## Dependencies

- `bottom-navigation-shell` (route `/my-artists` and tab must exist)

## Blocked By

- `bottom-navigation-shell`
