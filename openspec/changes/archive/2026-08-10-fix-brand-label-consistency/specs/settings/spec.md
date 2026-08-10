## ADDED Requirements

### Requirement: Settings Page Header Label
The Settings page header SHALL render the invariant English brand label "Settings" — the Layer B navigation tab label — rather than a locale-switched title string, so that the Settings header is consistent with its sibling tab pages whose headers all bind an invariant `nav.*` label.

#### Scenario: Header reads "Settings" regardless of active locale
- **WHEN** the Settings page is loaded with the active locale set to Japanese
- **THEN** the page header SHALL display "Settings"
- **AND** it SHALL NOT display a Japanese translation of the header (e.g. "設定")

#### Scenario: Header shares the navigation tab label source
- **WHEN** the Settings route renders its `page-header`
- **THEN** the header title SHALL resolve from the same invariant navigation label used by the bottom-navigation Settings tab (the `nav.settings` key, "Settings" in both JA and EN locales)
- **AND** the header SHALL NOT depend on a separate localized `settings.title` string
