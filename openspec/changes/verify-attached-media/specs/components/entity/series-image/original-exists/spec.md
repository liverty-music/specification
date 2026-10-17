## Purpose

SeriesImage.OriginalExists tells whether the original file uploaded for a SeriesImage exists under a given Organizer, which proves that Organizer uploaded it.

## ADDED Requirements

### Requirement: OriginalExists reports the uploaded original

OriginalExists SHALL take an Organizer id and a SeriesImage id and report whether the original uploaded for that SeriesImage under that Organizer exists. A file under another Organizer SHALL count as absent. It SHALL fail with Internal when storage cannot be read.

#### Scenario: Uploaded original
- **WHEN** an Organizer uploaded the original of a SeriesImage
- **THEN** OriginalExists reports true for that Organizer and that SeriesImage

#### Scenario: Another Organizer's upload
- **WHEN** the original of a SeriesImage was uploaded by another Organizer
- **THEN** OriginalExists reports false

#### Scenario: Nothing uploaded
- **WHEN** no original was uploaded for the SeriesImage, or it was already removed after processing
- **THEN** OriginalExists reports false
