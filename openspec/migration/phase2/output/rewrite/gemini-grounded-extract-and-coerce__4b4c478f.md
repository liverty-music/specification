<!-- spec: gemini-grounded-extract-and-coerce | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Discovered concert source URL prefers the tour-specific page -->

### Requirement: Discovered concert source URL prefers the tour-specific page

For each extracted tour or show, Step 1 SHALL set `source_url` to the artist's page dedicated to THAT specific tour/show — a tour special/feature page or the specific announcement article — in preference to the official-site top page or a generic news-list page, choosing the most detailed tour-specific candidate.

#### Scenario: Tour feature page preferred over the site top

- **WHEN** a tour has a dedicated feature page (e.g. a `/feature/<tour>` page) and the artist also has an official-site top page
- **THEN** `source_url` SHALL be the tour feature page, not the site top page

#### Scenario: No tour-specific page available

- **WHEN** no tour-specific page exists and only a general news-list or top page is available
- **THEN** Step 1 MAY use the most detailed available official page as `source_url`
