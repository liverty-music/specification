# Spec Delta

## MODIFIED Requirements

### Requirement: Discovery page debounces search with stale response guard
The Discovery screen SHALL send an artist search 2000 ms after the fan's last input in the search bar, or at once when the fan presses Enter (the keyboard's search key) there. An Enter that confirms an input method conversion SHALL NOT send a search. The screen SHALL search the query with leading and trailing white space removed, and SHALL NOT search an empty query or a query that is a single half-width Latin letter or digit; for such a single letter or digit it SHALL show neither results, nor loading, nor the no-results message. One query SHALL NOT be sent again while it is being answered or after it has been answered, until the query changes. A query whose search failed SHALL be sent again only when the fan presses Enter, until the query changes.

When the query changes, the fan clears it or the fan leaves Discovery, the screen SHALL cancel the search being answered, and nothing that search returns or fails with SHALL change the screen.

#### Scenario: Search is debounced
- **WHEN** the search query changes
- **THEN** no search request SHALL be sent until 2000 ms after the last change
- **AND** exactly one request SHALL be sent then

#### Scenario: Enter searches at once
- **WHEN** the fan presses Enter in the search bar 500 ms after typing a query
- **THEN** one search request SHALL be sent at once
- **AND** no second request SHALL be sent when 2000 ms have passed since the last input

#### Scenario: Enter on an answered query
- **WHEN** the fan presses Enter on a query that has already been answered
- **THEN** no search request SHALL be sent

#### Scenario: Enter that confirms a conversion
- **WHEN** the fan presses Enter to confirm a Japanese conversion in the search bar
- **THEN** no search request SHALL be sent at that moment

#### Scenario: Single letter or digit
- **WHEN** the query is `a` or `7` and 2000 ms pass or the fan presses Enter
- **THEN** no search request SHALL be sent
- **AND** neither results, loading nor the no-results message SHALL be shown

#### Scenario: Single non-Latin character
- **WHEN** the query is `嵐` and 2000 ms pass
- **THEN** a search request for `嵐` SHALL be sent

#### Scenario: Stale search response is discarded
- **WHEN** the search query changes again before a previous search responds
- **THEN** the previous search SHALL be cancelled
- **AND** its response SHALL be discarded

#### Scenario: Stale search fails after the newer one answered
- **WHEN** a newer search has shown its results and an earlier search then fails
- **THEN** the shown results SHALL stay
- **AND** no search-failure snack SHALL be shown

#### Scenario: Cleared or left while a search is outstanding
- **WHEN** the fan clears the query or leaves Discovery while a search is waiting to be sent or is being answered
- **THEN** no results and no search-failure snack SHALL appear for it

#### Scenario: Genre tag toggle activates and deactivates
- **WHEN** a genre chip is selected and then selected again
- **THEN** the first selection SHALL load the top artists of that genre and the second SHALL load the regional top artists with no genre

#### Scenario: Clear search restores Artists view
- **WHEN** the fan clears the search
- **THEN** the search query SHALL be emptied and the bubble canvas SHALL resume

## ADDED Requirements

### Requirement: Search shows its progress and outcome
The search mode, the clear button and the restored Artists view SHALL follow the query as the fan types, without waiting for the search to be sent. While a searchable query is waiting to be sent or is being answered, the screen SHALL show the results it already has, or a loading state when it has none, and SHALL NOT show the no-results message. A search that finds no artist, including one that fails with NotFound, SHALL show the no-results message and no snack. A search that fails otherwise SHALL clear the results, SHALL show neither loading nor the no-results message, and SHALL show a warning snack saying the search did not complete; at most one such snack SHALL be visible or waiting at a time.

#### Scenario: Typing before the search is sent
- **WHEN** the fan types the first characters of a query
- **THEN** search mode and the clear button SHALL appear at once
- **AND** the screen SHALL show the loading state, not the no-results message

#### Scenario: Refining a query with results
- **WHEN** results are shown and the fan types more characters
- **THEN** the shown results SHALL stay until the new search is answered

#### Scenario: No artist found
- **WHEN** the search fails with NotFound
- **THEN** the no-results message SHALL be shown
- **AND** no snack SHALL be shown

#### Scenario: Search times out
- **WHEN** the search fails with DeadlineExceeded
- **THEN** one warning snack saying the search did not complete SHALL be shown
- **AND** neither results, loading nor the no-results message SHALL be shown

#### Scenario: Searches fail one after another
- **WHEN** three searches in a row fail
- **THEN** at most one search-failure snack SHALL be visible or waiting

#### Scenario: Searching again after a failure
- **WHEN** a search has failed and the fan presses Enter on the same query
- **THEN** the query SHALL be sent again

#### Scenario: Input that keeps a failed query
- **WHEN** a search has failed and the fan only adds a space after the query, then 2000 ms pass
- **THEN** no search request SHALL be sent
