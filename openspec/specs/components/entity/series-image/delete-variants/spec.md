# components/entity/series-image/delete-variants Specification

## Purpose
SeriesImage.DeleteVariants removes every served size of a SeriesImage (the thumbnail and the large image).

## Requirements

### Requirement: DeleteVariants removes every served size

DeleteVariants SHALL remove every served size of the given SeriesImage, so none of its image URLs returns the image afterwards. Sizes that do not exist SHALL count as removed, so a repeated call succeeds. Any other failure SHALL be Internal.

#### Scenario: Served cover

- **WHEN** DeleteVariants runs for a SeriesImage with a thumbnail and a large image
- **THEN** neither exists afterwards

#### Scenario: Already removed

- **WHEN** no served size exists
- **THEN** DeleteVariants succeeds
