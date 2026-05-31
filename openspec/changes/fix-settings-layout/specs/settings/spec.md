## ADDED Requirements

### Requirement: Settings Page Layout and Scroll

The Settings page SHALL render a fixed page header and a vertically scrollable
content area. The settings section list SHALL scroll within the content area
without displacing or overlapping the fixed header, and the bottom navigation
bar SHALL remain unaffected. The content scroll container SHALL follow the
project's shared route scroll pattern: the content track grid item SHALL set
`min-block-size: 0` so it can shrink within its track, and scrolling SHALL be
owned by a scroll container whose minimum size does not prevent overflow.

#### Scenario: First preferences row is visible on load
- **WHEN** the Settings page loads
- **THEN** the PREFERENCES section title and its first row ("My Home Area")
  SHALL be visible within the content area
- **AND** they SHALL NOT be clipped by or rendered behind the fixed page header

#### Scenario: Section list scrolls within the content area
- **WHEN** the settings content exceeds the available viewport height
- **THEN** the section list SHALL scroll vertically within the content area
- **AND** the page header SHALL remain pinned at the top
- **AND** the bottom navigation bar SHALL remain pinned at the bottom

#### Scenario: Content track item can shrink
- **WHEN** the Settings route lays out its `header` / `content` grid
- **THEN** the content-area grid item SHALL set `min-block-size: 0`
- **AND** the scroll container SHALL engage `overflow-y: auto` rather than
  expanding the grid track to full content height
