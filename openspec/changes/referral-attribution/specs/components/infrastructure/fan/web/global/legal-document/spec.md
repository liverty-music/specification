## MODIFIED Requirements

### Requirement: Privacy Policy discloses the actual data practices

The Privacy Policy SHALL accurately disclose, at minimum: the categories of personal data collected; the purposes of use; third-party processors and any cross-border transfer; how to withdraw analytics consent; and the contact channel for disclosure / correction / deletion requests. The disclosure SHALL reflect the system's real integrations and SHALL be revised when a new third-party data integration is added.

For cross-border transfers, the Privacy Policy SHALL name each third-party recipient that receives personal data in a foreign country — including PostHog (operated by Klant Solutions B.V., Netherlands), to which usage analytics data is transferred (PostHog Cloud EU) — and SHALL, for that transfer, state the recipient's country (Netherlands), enumerate the categories of data transferred (interaction / usage events captured via cookies and localStorage), and state the purpose of the transfer (product analytics: improving the Service and measuring effectiveness). Whether any particular wording legally suffices under APPI Article 28 is a matter for the policy owner / legal counsel to confirm and is out of scope for this spec.

#### Scenario: Collected data and purposes are stated

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL list the collected personal data categories (account identity, home area, follows, language preference, push subscription, analytics events, purchase records — orders, tickets and the full name and phone number given for 本人確認 (identity check) — and the purchase route, that is the referral code of the link the fan came from when a purchase was started) and the purpose of each use

#### Scenario: Third-party transfer and cross-border processing are disclosed

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL identify third-party recipients / processors (analytics, email, push, search, artist-metadata)
- **AND** it SHALL disclose the cross-border transfer of analytics data to PostHog Cloud EU

#### Scenario: PostHog is named as a cross-border recipient with country, categories, and purpose

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL name PostHog (operated by Klant Solutions B.V.) as the recipient of a cross-border transfer of usage analytics data
- **AND** it SHALL state the recipient's country (Netherlands)
- **AND** it SHALL enumerate the categories of data transferred to PostHog (interaction / usage events captured via cookies and localStorage)
- **AND** it SHALL state the purpose of that transfer (product analytics: improving the Service and measuring effectiveness)

#### Scenario: Consent withdrawal and rights are explained

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL explain that analytics consent can be withdrawn via the Settings privacy toggles
- **AND** it SHALL provide a contact channel for disclosure / correction / deletion requests
