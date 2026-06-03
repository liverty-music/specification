## ADDED Requirements

### Requirement: Configure Login UI Branding

The system SHALL configure Liverty Music brand colors for the hosted Login UI v2 of the `liverty-music` product application, so its login flow presents product branding instead of the default Zitadel appearance. Because Zitadel defines branding only at instance or organization level (there is no application-level label policy), the system SHALL define an org-level label policy on the product org AND enforce it for the product application via the project's private-labeling setting. Branding SHALL be provisioned declaratively via the Zitadel Pulumi provider and activated.

#### Scenario: Brand colors on the product org label policy

- **WHEN** the Zitadel resources for the `liverty-music` product org are provisioned
- **THEN** a label policy SHALL be applied to that org with the Liverty Music brand colors (primary, background, font, warn — including dark variants) sourced from the product's brand palette
- **AND** the policy SHALL set `disableWatermark` so no Zitadel watermark is shown
- **AND** the policy SHALL be activated (set active) so the hosted Login UI v2 renders it

#### Scenario: Enforce product branding per application

- **WHEN** the product `Project` is provisioned
- **THEN** its private-labeling setting SHALL be `ENFORCE_PROJECT_RESOURCE_OWNER_POLICY`
- **AND** the product application's login flow SHALL render the product org's label policy regardless of the logging-in user's organization
- **AND** the separate admin/console org login SHALL remain unaffected (it is a different org)

#### Scenario: Hosted Login UI v2 reflects the brand colors

- **WHEN** an end user reaches the hosted login screen (`/ui/v2/login/*`) through the product OIDC flow
- **THEN** the screen SHALL display the Liverty Music brand colors (buttons, links, background, text)
- **AND** it SHALL NOT display the default unbranded Zitadel colors or watermark

#### Scenario: Light and dark themes are branded

- **WHEN** the login screen is rendered in either light or dark mode
- **THEN** the corresponding brand colors SHALL be applied for that theme

#### Scenario: Logo and login text remain out of scope

- **WHEN** the login branding is applied
- **THEN** only brand colors and theme SHALL be customized
- **AND** no login logo SHALL be set (deferred until a brand logo asset exists)
- **AND** login interface text strings SHALL remain the Zitadel Login UI v2 defaults (text customization is out of scope for this capability change)
