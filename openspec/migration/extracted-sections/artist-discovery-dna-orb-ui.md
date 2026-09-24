<!-- Extracted 2026-09-21 from openspec/specs/artist-discovery-dna-orb-ui/spec.md lines 317-330.
     Non-product sections removed so the spec has only Purpose and Requirements.
     Sections: Technical Context, Reference Documentation
     Routed in Phase 1 manifest (OUT:design-doc / OUT:delete). -->

## Technical Context

This specification defines the Artist Discovery UI for Liverty Music MVP, featuring:
- **UI Metaphor**: "DNA Extraction" - collecting user music preferences as genetic material
- **Core Component**: Music DNA Orb (glass sphere) that visually accumulates user taste
- **Data Source**: Backend `ArtistService` RPCs (`ListTop`, `ListSimilar`) via Connect-RPC
- **Animation Requirements**: Physics-based bubbles, absorption effects, particle systems
- **Performance Target**: Smooth 60fps on mobile devices

## Reference Documentation

For detailed visual design, animation specs, and UI behavior, see:
- `../../changes/archive/2026-02-15-frontend-artist-discovery-ui/docs/onboarding-ux.md` (Japanese detailed specification - Step 2)
