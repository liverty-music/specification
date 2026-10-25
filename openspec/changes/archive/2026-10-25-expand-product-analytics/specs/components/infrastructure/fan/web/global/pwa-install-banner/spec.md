## ADDED Requirements

### Requirement: Showing the banner and installing are reported

The fan app SHALL send one usage analytics event each time the install banner is shown, one with the fan's answer when the fan starts the install from the banner (accepted or dismissed in the device's install request, or the manual guide opened where the device offers no request), and one when the app is installed, whatever started the install.

#### Scenario: Install from the banner
- **WHEN** the banner is shown and the fan installs the app from the device's install request
- **THEN** a banner-shown event, an accepted answer and an installed event are sent
