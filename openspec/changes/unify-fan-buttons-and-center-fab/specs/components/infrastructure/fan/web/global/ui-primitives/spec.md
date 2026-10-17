## ADDED Requirements

### Requirement: One button style in four variants

Every text button in the fan app SHALL use one shared button style, in one of four variants. All four SHALL share the same corner radius (12px), padding and label weight, so that any text button reads as a button from its shape alone. Icon-only buttons are not covered by this requirement.

- **filled** (the default): a solid brand-primary fill with white text, for the main action on a screen.
- **outlined**: a transparent fill with a visible border, for secondary and dismissive actions (cancel, later, back).
- **danger**: a solid red fill with white text, for destructive actions.
- **on-container**: a translucent white fill with a white border, for a button placed on a coloured surface such as a snack bar or a banner.

A text button SHALL NOT be rendered as plain text without a fill or a border.

#### Scenario: Default variant
- **WHEN** a text button is rendered without a variant
- **THEN** it SHALL have a brand-primary fill, white text and a 12px corner radius

#### Scenario: Secondary and dismissive actions are outlined
- **WHEN** a screen offers a cancel, later or back action next to its main action
- **THEN** that action SHALL be rendered in the outlined variant with a visible border

#### Scenario: Destructive action
- **WHEN** a button cancels an entry or deletes data
- **THEN** it SHALL be rendered in the danger variant

#### Scenario: Button on a coloured surface
- **WHEN** a button is placed on a snack bar or a banner with a coloured or gradient fill
- **THEN** it SHALL be rendered in the on-container variant with a translucent white fill and a white border at least 1.5px wide

#### Scenario: Catalog matches the specification
- **WHEN** the button catalog shows all four variants side by side
- **THEN** each variant SHALL render as described above, and any change to their look SHALL be detected by comparing the catalog with its approved screenshot
