## Why

The onboarding flow currently lacks an engaging artist discovery step. Users need an intuitive, gamified way to select their favorite artists so the platform can personalize concert recommendations. A "DNA Extraction" metaphor with physics-based bubble interactions and a visual DNA Orb creates a memorable first experience that drives higher artist follow rates.

## What Changes

- Add a new Artist Discovery UI step to the onboarding flow featuring an interactive DNA Orb (glass sphere) and physics-based artist bubbles
- Implement bubble absorption animations when users tap artist bubbles, with visual feedback flowing into the DNA Orb
- Integrate Last.fm `artist.getSimilar` API to dynamically spawn related artist recommendations as chain reactions
- Display dynamic toast notifications when followed artists have upcoming live events
- Provide a completion action via the DNA Orb to navigate users to their personalized live schedule

## Capabilities

### New Capabilities
- `artist-discovery-dna-orb-ui`: Interactive artist discovery interface with DNA Orb metaphor, physics-based bubbles, absorption animations, similar artist chain reactions, and live event toast notifications

### Modified Capabilities
- `frontend-onboarding-flow`: Adding the Artist Discovery step as a new stage in the onboarding sequence, between authentication and the loading/dashboard screen

## Impact

- **Frontend**: New Aurelia 2 components for the DNA Orb, bubble physics, animations, and toast notifications
- **APIs**: Integration with Last.fm API (`geo.getTopArtists`, `artist.getSimilar`) and backend artist-following / live-events services
- **Dependencies**: Physics engine library (Matter.js or D3 force simulation), WebGL/Canvas for performant rendering
- **Performance**: Must maintain 60fps on mobile devices; requires optimization with memoization and efficient rendering strategies
