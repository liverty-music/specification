## ADDED Requirements

### Requirement: Type-scale minimum legibility floor
The design system SHALL keep all body and label text at or above a legible minimum size by setting the type-scale floor token `--step--2` to a minimum of 11px and resting the app-wide visible text floor on `--step--1`. The `--step--2` token SHALL be treated as a compact-only exception, used solely by components that are intentionally dense.

#### Scenario: Minimum floor token raised to 11px
- **WHEN** the design tokens are defined in `tokens.css`
- **THEN** `--step--2` SHALL resolve to a minimum of 11px (`clamp(0.6875rem, calc(0.6rem + 0.13vi), 0.7rem)`)
- **AND** the minimum end SHALL sit on the modular type-scale curve (11px ≈ 16 ÷ 1.2²)

#### Scenario: General text rests on --step--1 or larger
- **WHEN** a component renders body, label, caption, or chip text
- **THEN** it SHALL use `--step--1` (13.3–16px) or a larger step
- **AND** it SHALL NOT use `--step--2` unless it is one of the documented compact-only exceptions

#### Scenario: --step--2 scoped to compact-only components
- **WHEN** `--step--2` is referenced for `font-size`
- **THEN** the only permitted consumers SHALL be the bottom navigation bar labels and the my-artists hype-column headers (including their inline `small` text)
- **AND** all other prior `--step--2` consumers SHALL reference `--step--1` instead
