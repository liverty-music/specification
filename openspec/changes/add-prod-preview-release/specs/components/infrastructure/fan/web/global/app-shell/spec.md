## ADDED Requirements

### Requirement: The fan web app served from the preview address calls the preview API

Production serves a release to the owner on a preview address before fans receive it: the fan web app at `https://preview.liverty-music.app` and the fan API at `https://api.preview.liverty-music.app`. When the fan web app is loaded from the preview address, it SHALL send every request to the preview API address, whatever `apiBaseUrl` in `/config.json` says, so that a new web app is always checked together with the new API it will run beside. The same files serve the production address after the release is promoted, so the choice SHALL be made from the address the page was loaded from and not from a value fixed in `/config.json`.

When the page is loaded from any other address, `apiBaseUrl` from `/config.json` SHALL be used as before.

The environment check that compares `/config.json`'s `environment` with the address SHALL treat the preview address as a production address: a production configuration passes, and any other `environment` stops startup with the same error page as any other mismatch.

#### Scenario: Loaded from the preview address

- **WHEN** the fan web app is loaded from `https://preview.liverty-music.app`
- **AND** `/config.json` has `apiBaseUrl` `https://api.liverty-music.app`
- **THEN** every request the app sends to the backend goes to `https://api.preview.liverty-music.app`

#### Scenario: Loaded from the production address

- **WHEN** the fan web app is loaded from `https://liverty-music.app`
- **THEN** every request the app sends to the backend goes to the `apiBaseUrl` of `/config.json`

#### Scenario: Production configuration on the preview address

- **WHEN** the fan web app is loaded from `https://preview.liverty-music.app`
- **AND** `/config.json` has `environment` `prod`
- **THEN** startup continues

#### Scenario: Other environment's configuration on the preview address

- **WHEN** the fan web app is loaded from `https://preview.liverty-music.app`
- **AND** `/config.json` has `environment` `dev`
- **THEN** startup stops with the static error page naming the environment mismatch
