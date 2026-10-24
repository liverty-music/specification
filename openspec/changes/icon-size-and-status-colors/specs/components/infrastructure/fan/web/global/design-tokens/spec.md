## ADDED Requirements

### Requirement: Status colors are named by meaning

A status SHALL be colored by its meaning, through one token per meaning: done or verified uses the success color, selected uses the primary role, a warning uses the warning color, and an error uses the error color. The same meaning SHALL use the same color on every screen, and every color a stylesheet references SHALL be a defined token. The success color SHALL stay green and SHALL be distinguishable from the brand accent and the stage colors: at least 0.1 apart in OKLab from each.

#### Scenario: Done looks the same everywhere

- **WHEN** a screen shows that something is done or verified (an email address verified, an identity verified, a ticket paid)
- **THEN** its status mark uses the success color

#### Scenario: Selected is not shown as done

- **WHEN** a list marks the item the fan has chosen (a followed artist in Discovery, the current language)
- **THEN** the mark uses the primary color, not the success color

#### Scenario: No undefined color

- **WHEN** the stylesheets are checked
- **THEN** every `--color-*` they reference is defined by the tokens

#### Scenario: Success is not the brand accent

- **WHEN** the success color and the brand accent are compared
- **THEN** they are at least 0.1 apart in OKLab, and so are the success color and each stage color
