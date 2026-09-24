# Artist.FetchImage

## Purpose

Obtains and reads the logo image at a URL of the image catalog, so it can be analyzed.

## Requirements

### Requirement: FetchImage returns the image or none
FetchImage SHALL return the image at the given URL. When the image catalog reports that no image exists at the URL, FetchImage SHALL return no image and no error.

#### Scenario: Image exists
- **WHEN** FetchImage is called with the URL of an existing logo
- **THEN** it returns the image

#### Scenario: No image at the URL
- **WHEN** the image catalog reports that no image exists at the URL
- **THEN** FetchImage returns no image and no error

### Requirement: FetchImage accepts only secure image-catalog URLs
FetchImage SHALL fail with InvalidArgument, without contacting any host, when the URL is malformed, does not use HTTPS, or does not point to the image catalog's host.

#### Scenario: Non-HTTPS URL
- **WHEN** FetchImage is called with an HTTP URL
- **THEN** FetchImage fails with InvalidArgument

#### Scenario: Foreign host
- **WHEN** FetchImage is called with an HTTPS URL on a host other than the image catalog's
- **THEN** FetchImage fails with InvalidArgument

### Requirement: FetchImage reports transfer and reading failures
FetchImage SHALL fail with Unavailable when the host cannot be reached or answers with an error other than a missing image, and with Internal when the returned data cannot be read as an image.

#### Scenario: Host error
- **WHEN** the image host answers with a server error
- **THEN** FetchImage fails with Unavailable

#### Scenario: Unreadable data
- **WHEN** the data at the URL is not an image
- **THEN** FetchImage fails with Internal
