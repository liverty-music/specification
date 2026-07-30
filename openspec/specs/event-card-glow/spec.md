# Event Card Glow

## Purpose

This capability defines the visual glow effect applied to matched event cards on the dashboard. The glow effect uses a diffuse laser-beam style around the card border to indicate a match, while remaining visually subdued so it does not overwhelm surrounding content.

---

## Requirements

### Requirement: Matched event card glow opacity
The dashboard matched event card (`[data-matched]`) SHALL render a diffuse laser-beam glow effect around its border using `--_spot-glow` at alpha 50% or lower so that the glow does not visually overwhelm surrounding content.

#### Scenario: Matched card glow is visually subdued
- **WHEN** a concert card has the `data-matched` attribute
- **THEN** the surrounding box-shadow glow SHALL use an alpha value of 50% or lower for the diffuse layers
