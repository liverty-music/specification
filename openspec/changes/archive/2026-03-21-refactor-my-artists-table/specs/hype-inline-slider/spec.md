## REMOVED Requirements

### Requirement: Sticky Header Legend

**Reason**: The detached `<header class="hype-legend">` + shared `grid-template-columns` sync pattern is replaced by a proper `<thead>` with `<th scope="col">` elements inside the `<table>`. Column alignment is guaranteed structurally by the table layout engine, not by duplicated CSS grid definitions.

**Migration**: Remove `<header class="hype-legend">` from `my-artists-route.html`. Remove `.hype-legend` and `.hype-legend-item` CSS rules. Hype column labels move to `<th scope="col">` in `<thead>`.

### Requirement: Inline Dot Slider

**Reason**: The `hype-inline-slider` custom element is deleted. Its visual output (dot radio stops, track line, glow effects) is now rendered directly in the `<table>` cells of `my-artists-route.html`. The `<fieldset>/<legend>` pattern for grouping radio inputs is superseded by `<table>` column/row headers which provide the same semantic association automatically.

**Migration**: Delete `src/components/hype-inline-slider/hype-inline-slider.ts`, `.html`, and `.css`. Move `.hype-slider-dot` styles and `@keyframes dot-pulse` to `my-artists-route.css`. The `<fieldset>` now wraps the entire table (see `my-artists` spec).

### Requirement: Slider dot positions align with header columns

**Reason**: Column alignment is now inherent to `<table>` layout. No CSS grid synchronisation is needed.

**Migration**: Remove `grid-template-columns: 2fr repeat(4, 1fr)` from `hype-inline-slider`, `artist-row-content`, and `hype-legend`. Table column widths handle alignment automatically.
