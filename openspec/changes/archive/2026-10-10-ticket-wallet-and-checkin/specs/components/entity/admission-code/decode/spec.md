# Spec Delta

## Purpose

Reads the text of a scanned QR code into an AdmissionCode, without yet trusting it.

## ADDED Requirements

### Requirement: Decode reads the code's content without trusting it

Decode SHALL take the scanned text and return the AdmissionCode it carries — user, event, tickets, signed time and signature — when the text has the AdmissionCode format and describes a valid code, and SHALL report Malformed otherwise. Decode SHALL not fail for any text and SHALL not check the signature.

#### Scenario: Code from the tickets screen

- **WHEN** the text of a fan's entry QR code is decoded
- **THEN** its user, event, tickets, signed time and signature are returned

#### Scenario: Ordinary QR code

- **WHEN** a QR code holding a web address is decoded
- **THEN** Decode reports Malformed

#### Scenario: Too many tickets

- **WHEN** the text describes a code presenting 11 Tickets
- **THEN** Decode reports Malformed
