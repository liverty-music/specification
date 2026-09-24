<!-- Extracted 2026-09-21 from openspec/specs/dna-orb-color-injection/spec.md lines 57-95.
     Non-product sections removed so the spec has only Purpose and Requirements.
     Sections: Test Cases
     Routed in Phase 1 manifest (OUT:design-doc / OUT:delete). -->

## Test Cases

### Unit Tests (Vitest — orb-renderer.spec.ts)

#### TC-ORB-01: injectColor preserves particle count

- **Given** an OrbRenderer initialized with `maxParticles = 60`
- **When** `injectColor(142)` is called
- **Then** `particles.length` SHALL remain 60
- **And** at least 5 particles SHALL have hue within ±10 of 142

#### TC-ORB-02: swirlIntensity set to 1.0 after injectColor

- **Given** an OrbRenderer with `swirlIntensity = 0`
- **When** `injectColor(200)` is called
- **Then** `swirlIntensity` SHALL be `1.0`

#### TC-ORB-03: swirlIntensity decays to 0 after sufficient updates

- **Given** an OrbRenderer after `injectColor(100)` (`swirlIntensity = 1.0`)
- **When** `update(100)` is called 12 times (1200ms total, >1000ms decay window)
- **Then** `swirlIntensity` SHALL be `0`

#### TC-ORB-04: Multiple rapid injectColor calls inject each hue

- **Given** an OrbRenderer
- **When** `injectColor(100)` then `update(200)` then `injectColor(300)` are called
- **Then** `swirlIntensity` SHALL restart to `1.0` on the second call
- **And** particles SHALL contain hues near both 100 and 300

### Unit Tests (Vitest — dna-orb-canvas.spec.ts)

#### TC-ORB-05: Absorption completion threads hue to OrbRenderer

- **Given** a DnaOrbCanvas handling an artist interaction
- **When** `startAbsorption()` is called
- **Then** it SHALL receive the artist's hue and an `onComplete` callback
- **And** when the absorption completes, `orbRenderer.injectColor(hue)` SHALL be called
