# SeriesImage

## Purpose

A SeriesImage is an image an Organizer uploaded for one of its Series, served to fans only as processed variants: a thumbnail at most 800 px wide and a large image at most 1920 px wide. The original upload is never served.

| attribute | meaning | constraint |
|-----------|---------|------------|
| id | series image identifier, also the version of its served addresses | required |
| organizer | the Organizer that uploaded it | required |
| thumb | address of the thumbnail variant | required when shown as a cover |
| large | address of the large variant | required when shown as a cover |

```mermaid
erDiagram
  Organizer ||--o{ SeriesImage : "uploads"
  Series |o--o| SeriesImage : "has cover"
```

## Requirements

### Requirement: A shown image exposes both variants

A SeriesImage, when shown as a Series cover, SHALL expose both a thumb and a large variant address.

#### Scenario: Cover with both variants
- **WHEN** a Series cover is an IMAGE with thumb and large addresses
- **THEN** the cover is valid

#### Scenario: Cover missing a variant
- **WHEN** a Series cover is an IMAGE with only a thumb address
- **THEN** the cover is invalid

### Requirement: Served addresses are stable per series image

The variant addresses of a SeriesImage SHALL be derived from its Organizer and id and SHALL never change; a replaced cover gets a new SeriesImage with new addresses.

#### Scenario: Replacing the cover
- **WHEN** a Series' cover is replaced by a new upload
- **THEN** the new cover is a different SeriesImage with different variant addresses
