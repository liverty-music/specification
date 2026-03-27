## REMOVED Requirements

### Requirement: Artist count in page header

**Reason**: The artist count badge `(N)` in the My Artists page header is not defined in any specification. It adds visual clutter without meaningful utility — the count is self-evident from the list itself.

**Migration**: Remove the `<span class="artist-count">` element from `my-artists-route.html` and any associated CSS rules.
