## REMOVED Requirements

### Requirement: Must Go Mutation UI
**Reason**: Replaced by the hype-lane match model in `passion-level` capability. The "Must Go" concept mapped to the old passion-level terminology. The new model uses `isHypeMatched(hype, lane)` to determine card prominence, which generalizes the mutation logic to all hype tiers (not just "Must Go").
**Migration**: Remove Must Go badge, expanded card, and ring border logic. Card prominence is now controlled by the `data-matched` attribute driven by hype-lane match computation.

### Requirement: Mutation Layout Handling
**Reason**: With the match model, cards do not change size or layout — only saturation, border, glow, and texture change. No special layout accommodation is needed.
**Migration**: Remove mutation-specific layout rules. Standard lane layout handles all cards uniformly.
