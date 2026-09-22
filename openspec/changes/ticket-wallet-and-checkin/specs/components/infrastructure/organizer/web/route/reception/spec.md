## Purpose

Provides the reception screen staff use to scan a fan's entry credential with a device camera and admit them, running as an installable web app with no dedicated scanner hardware or native app required.

## ADDED Requirements

### Requirement: Reception check-in PWA (web camera)

The system SHALL provide a **reception PWA** that scans the QR using the **web
camera (`getUserMedia`)** — no native app, no NFC reader hardware — and performs
the server validation + atomic duplicate-check above.

#### Scenario: Reception runs in the browser

- **WHEN** reception is opened
- **THEN** it captures the camera via getUserMedia in a PWA with no native app install and no NFC reader hardware
