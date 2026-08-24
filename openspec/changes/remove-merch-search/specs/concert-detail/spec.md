## REMOVED Requirements

### Requirement: Merch Info Link in Concert Detail

**Reason**: The `Series.merch_url` field is removed, so the concert detail sheet no longer has a merchandise link to render. Production data showed the resolved link was usually a generic storefront/homepage rather than a tour-specific goods page, offering no value beyond the existing official-info link.

**Migration**: None. The "View Merch Info / グッズ情報を見る" link, its `eventDetail.viewMerch` i18n keys, the `hasMerchUrl` gate, and the `merchUrl` client entity field are removed. The official-info link is unchanged.

## MODIFIED Requirements

### Requirement: Localized Concert Detail Sheet Copy

The frontend SHALL render all user-facing text in the concert detail sheet via i18n keys under a dedicated `eventDetail.*` namespace, with parallel JA and EN translations in `frontend/src/locales/<locale>/translation.json`. No literal English (or any other language) text SHALL be embedded directly in the `event-detail-sheet.html` template.

#### Scenario: Static labels are i18n-keyed

- **WHEN** the concert detail sheet renders any static label (date/time row prefix, action button text, ticket-status section heading, removal button)
- **THEN** the label SHALL be sourced from an `eventDetail.*` i18n key
- **AND** the JA and EN translation files SHALL both contain a value for that key
- **AND** the displayed string SHALL match the locale resolved by `@aurelia/i18n`

#### Scenario: Required i18n keys

- **WHEN** the concert detail sheet is implemented
- **THEN** the following `eventDetail.*` keys SHALL be defined in both JA and EN translation files:
  - `eventDetail.ariaLabel` — the sheet's `aria-label`
  - `eventDetail.openStart` — the open/start time line with `{{open}}` and `{{start}}` interpolation placeholders. When the open time is unknown, the `{{open}}` slot SHALL be filled with the em-dash character `—` (U+2014) supplied directly by the component (locale-invariant; not routed through an i18n key).
  - `eventDetail.openInGoogleMaps` — the Google Maps link label
  - `eventDetail.ticketStatus` — the ticket-status section heading
  - `eventDetail.stopTracking` — the "remove ticket journey" button label
  - `eventDetail.viewOfficialInfo` — the official info link label
  - `eventDetail.addToCalendar` — the add-to-calendar link label

#### Scenario: Journey status enum values are i18n-keyed

- **WHEN** the concert detail sheet renders a `TicketJourneyStatus` value as a button label or as the currently-displayed status
- **THEN** the surface form SHALL be sourced from a sub-namespace `eventDetail.journeyStatus.<value>` rather than the raw enum string
- **AND** the JA and EN translation files SHALL both contain values for every supported `TicketJourneyStatus` value (currently `tracking`, `applied`, `lost`, `unpaid`, `paid`)
- **AND** the raw enum string SHALL NOT appear in the rendered UI

#### Scenario: Adding a new TicketJourneyStatus value

- **WHEN** a new value is added to the `TicketJourneyStatus` type
- **THEN** the change SHALL add a corresponding `eventDetail.journeyStatus.<newValue>` entry to both the JA and EN translation files
- **AND** the absence of either locale value SHALL be a defect
