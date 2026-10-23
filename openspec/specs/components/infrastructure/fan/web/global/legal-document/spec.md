# Legal Document

## Purpose

Defines the in-app Terms of Service, Privacy Policy, and OSS Licenses pages: their stable routes, guest reachability, ja/en localization, the required disclosure content for each document, and the build-time auto-generation of the OSS license list.

## Requirements

### Requirement: Privacy Policy discloses the actual data practices

The Privacy Policy SHALL accurately disclose, at minimum: the categories of personal data collected; the purposes of use; third-party processors and any cross-border transfer; how to withdraw analytics consent; and the contact channel for disclosure / correction / deletion requests. The disclosure SHALL reflect the system's real integrations and SHALL be revised when a new third-party data integration is added.

For cross-border transfers, the Privacy Policy SHALL name each third-party recipient that receives personal data in a foreign country — including PostHog (operated by Klant Solutions B.V., Netherlands), to which usage analytics data and error reports are transferred (PostHog Cloud EU) — and SHALL, for that transfer, state the recipient's country (Netherlands), enumerate the categories of data transferred (interaction / usage events captured via cookies and localStorage, and error reports: what failed, on which screen, and the steps before it), and state the purposes of the transfer (product analytics: improving the Service and measuring effectiveness; 不具合の検出と修正, detecting and fixing defects). Whether any particular wording legally suffices under APPI Article 28 is a matter for the policy owner / legal counsel to confirm and is out of scope for this spec.

#### Scenario: Collected data and purposes are stated

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL list the collected personal data categories (account identity, home area, follows, language preference, push subscription, analytics events, error reports, purchase records — orders, tickets and the full name and phone number given for 本人確認 (identity check) — and the purchase route, that is the referral code of the link the fan came from when a purchase was started) and the purpose of each use
- **AND** the purposes SHALL include 不具合の検出と修正 (detecting and fixing defects)

#### Scenario: Third-party transfer and cross-border processing are disclosed

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL identify third-party recipients / processors (analytics, email, push, search, artist-metadata)
- **AND** it SHALL disclose the cross-border transfer of analytics data to PostHog Cloud EU

#### Scenario: PostHog is named as a cross-border recipient with country, categories, and purpose

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL name PostHog (operated by Klant Solutions B.V.) as the recipient of a cross-border transfer of usage analytics data and error reports
- **AND** it SHALL state the recipient's country (Netherlands)
- **AND** it SHALL enumerate the categories of data transferred to PostHog (interaction / usage events captured via cookies and localStorage, and error reports)
- **AND** it SHALL state the purposes of that transfer (product analytics: improving the Service and measuring effectiveness; 不具合の検出と修正)

#### Scenario: Consent withdrawal and rights are explained

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL explain that analytics consent can be withdrawn via the Settings privacy toggles, and that turning off the product-analytics toggle also stops error reports
- **AND** it SHALL provide a contact channel for disclosure / correction / deletion requests

### Requirement: Terms of Service disclaims third-party data accuracy

The Terms of Service SHALL include, at minimum: the service description, account and prohibited-conduct terms, a disclaimer that third-party-sourced concert / ticket / sales information is not guaranteed accurate or current, limitation of liability, and governing law / jurisdiction.

#### Scenario: Third-party data disclaimer present

- **WHEN** the Terms of Service is displayed
- **THEN** it SHALL state that concert, ticket, and sales-timing information originates from third parties and is provided without a guarantee of accuracy or timeliness

### Requirement: OSS Licenses content is generated from the shipped dependencies

The OSS Licenses page content SHALL be generated at build time from the production dependency tree, listing each bundled third-party package with its license and required attribution, so that the displayed list reflects what is actually distributed and does not require manual maintenance.

#### Scenario: License list reflects the production bundle

- **WHEN** the OSS Licenses page is displayed
- **THEN** it SHALL list the third-party packages included in the production build with their license names and attribution / copyright notices

#### Scenario: List regenerates on dependency change

- **WHEN** the production dependency set changes and the app is rebuilt
- **THEN** the OSS Licenses content SHALL regenerate to match the new dependency set

### Requirement: Terms of Service state the official resale rules

The Terms of Service SHALL include an official resale (公式リセール) article stating:
- that resale through the platform at face value is the only resale the Organizer consents to;
- that resale opens for a first-come sale only when it sells out, and that a fan who cannot attend an event that does not sell out has no resale and no refund except when the event is 中止 (cancelled);
- that listing closes when the event's admission opens, 3 hours before the start time, and that an unsold ticket stays the fan's and remains valid;
- that a listed ticket can be withdrawn until another fan starts buying it, and that a sale is not guaranteed;
- that when the ticket sells, it becomes invalid, a new ticket is issued to the purchasing fan, and the listing fan is refunded the face value minus a resale fee of 10% to the card they paid with;
- that when a concert is cancelled after a resale, the resold ticket's fee is not returned.

#### Scenario: Resale article present
- **WHEN** the Terms of Service is displayed
- **THEN** it states when resale opens and closes, that an event that does not sell out has no resale, the 10% resale fee, and how the refund is made
