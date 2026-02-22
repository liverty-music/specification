# Proposal: Passion Level

## Problem

Currently, all followed artists are treated equally on the Dashboard. Users have no way to express different levels of enthusiasm for different artists. A die-hard fan willing to travel nationwide for a concert and a casual listener interested only in local events both see the same Dashboard layout. This means users might miss "must-go" concerts in distant cities or be overwhelmed by noise from artists they only casually follow.

## Solution

Introduce a **Passion Level** system with three tiers:

- 🔥🔥 **Must Go** — Will travel anywhere. Events appear prominently across all Dashboard lanes.
- 🔥 **Local Only** — Default. Events shown normally in nearby lanes only.
- 👀 **Keep an Eye** — Display on Dashboard but exclude from push notifications.

On the **My Artists page**, add a per-artist passion level selector.

On the **Dashboard (Live Highway)**, introduce **Visual Mutation UI**: when a "Must Go" artist has an event in Lane 2 or Lane 3, the card breaks out of the normal compact rendering and becomes a large, visually striking "expedition alert" card.

## Scope

### In Scope

- Passion Level data model (frontend + backend persistence)
- Per-artist passion level selector on My Artists page
- Dashboard Mutation UI for Must Go artists in Lane 2/3
- Backend API for setting/getting passion level per followed artist
- Grid/Festival view toggle on My Artists page (フェス風ポスター表示)

### Out of Scope

- Push notification filtering by passion level (can be a follow-up)

## Impact

- New spec: `passion-level`
- Modified spec: `typography-focused-dashboard` (Mutation UI addition)
- Modified spec: `artist-following` (passion level field on follow relationship, ListFollowed response enrichment)
- Modified spec: `my-artists` (passion level indicator and selector UI)
- New backend API endpoint (`SetPassionLevel` RPC)
- Breaking change: `ListFollowedResponse` schema (`Artist` → `FollowedArtist`)

## Dependencies

- `my-artists` (passion level selector is added to the artist list rows)
- `artist-following` (follow relationship must exist to attach passion level)

## Blocked By

- `my-artists` (page must exist before adding passion selector)
