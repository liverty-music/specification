# Spec Delta

## Purpose

Media.DeleteOriginal removes the original file uploaded for a Media.

## ADDED Requirements

### Requirement: DeleteOriginal removes the uploaded file

DeleteOriginal SHALL remove the original file of the given Media. A file that does not exist SHALL count as removed, so a repeated call succeeds. Any other failure SHALL be Internal.

#### Scenario: Uploaded original

- **WHEN** DeleteOriginal runs for a Media whose original exists
- **THEN** the original no longer exists

#### Scenario: Already removed

- **WHEN** the original does not exist
- **THEN** DeleteOriginal succeeds
