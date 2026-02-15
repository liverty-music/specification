## Why

After the Artist Discovery step, the system needs to aggregate live event data for all followed artists before rendering the Dashboard. This involves querying the internal database and potentially invoking Gemini API for artists without existing event data — a process that takes 3-10 seconds. Without a purposeful loading experience, users face a blank screen or simple spinner, creating anxiety and drop-off risk at the most critical moment of the onboarding flow.

## What Changes

- **New Loading Sequence component**: A multi-phase animated loading screen with progressive messaging ("Building your Music DNA..." → "Cross-referencing live schedules..." → "AI searching for latest tour info...").
- **Backend data aggregation trigger**: Frontend calls `SearchNewConcerts` for each followed artist that lacks concert data, with a 10-second global timeout.
- **Minimum display duration**: Enforce a 3-second minimum display time even if data loads faster, ensuring the "benevolent deception" effect.
- **Graceful degradation**: If the timeout fires, proceed to Dashboard with whatever data was successfully retrieved.

## Capabilities

### New Capabilities
- `loading-sequence`: The animated loading screen UI, data aggregation orchestration, timeout handling, and transition to Dashboard.

### Modified Capabilities
- `frontend-onboarding-flow`: Update flow to include Loading Sequence as the transition between Artist Discovery and Dashboard.

## Impact

- **Frontend**: New Aurelia 2 component for the loading sequence. Route addition at `/onboarding/loading`.
- **Backend**: No new endpoints — uses existing `SearchNewConcerts` and `ListFollowedArtists` RPCs.
- **UX**: Critical flow step that bridges Artist Discovery → Dashboard with engagement rather than dead time.
