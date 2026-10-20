## MODIFIED Requirements

### Requirement: One button style in four variants

Every text button in the fan app SHALL use one shared button style, in one of four variants. All four SHALL share the same corner radius (12px), padding and label weight, so that any text button reads as a button from its shape alone. The one exception is the action on a snack bar or a bottom banner, which SHALL use a compact size (a smaller label and padding, 36px tall) with the same radius and weight, so the message keeps the width of its row. On a bottom banner the compact button's label SHALL take the banner's own text size, the same as the message, and its fill SHALL be darkened in brand-primary's hue so that the smaller white label still measures at least 4.5:1. Icon-only buttons are not covered by this requirement.

- **filled** (the default): a solid brand-primary fill with white text, for the main action on a screen and, with the darker fill above, the action on a bottom banner.
- **outlined**: a transparent fill with a visible border, for secondary and dismissive actions (cancel, later, back).
- **danger**: a solid red fill with white text, for destructive actions.
- **on-container**: a translucent white fill with a white border, for a button placed on a coloured surface such as a snack bar.

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
- **WHEN** a button is placed on a snack bar with a coloured or gradient fill
- **THEN** it SHALL be rendered in the on-container variant with a translucent white fill and a white border at least 1.5px wide

#### Scenario: Compact button on a snack bar
- **WHEN** a snack bar shows an action
- **THEN** the action SHALL be 36px tall with a label smaller than the default button's
- **AND** it SHALL keep the shared 12px corner radius and the bold label weight

#### Scenario: Compact filled button on a bottom banner
- **WHEN** the install banner or the signup prompt shows its action
- **THEN** the action SHALL be the filled variant, 36px tall, with its fill darkened in brand-primary's hue so that the white label measures at least 4.5:1
- **AND** its label SHALL have the same text size as the banner's message
- **AND** it SHALL keep the shared 12px corner radius and the bold label weight

#### Scenario: Catalog matches the specification
- **WHEN** the button catalog shows all four variants side by side
- **THEN** each variant SHALL render as described above, and any change to their look SHALL be detected by comparing the catalog with its approved screenshot
