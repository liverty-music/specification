<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner CTA Install Flow by Platform -->
<!-- implementation names to remove: PwaInstallService -->

### Requirement: Banner CTA Install Flow by Platform

The banner SHALL trigger the appropriate install action based on platform and available deferred prompt.

#### Scenario: Native one-tap install (Chrome/Edge with deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** `PwaInstallService.canShowFab` is `true` (deferred prompt captured, not iOS)
- **THEN** the system SHALL call `deferredPrompt.prompt()`
- **AND** the native browser install dialog SHALL appear

#### Scenario: Guide sheet (iOS Safari or no deferred prompt)

- **WHEN** the user taps the CTA button
- **AND** `PwaInstallService.canShowFab` is `false` (iOS Safari or deferred prompt not yet captured)
- **THEN** the system SHALL open a bottom sheet containing step-by-step install instructions

#### Scenario: iOS guide sheet content

- **WHEN** the guide sheet is shown
- **AND** the platform is iOS (`PwaInstallService.isIos` is `true`)
- **THEN** the sheet SHALL display:
  1. Safari の共有ボタン（□↑）をタップ
  2. 「ホーム画面に追加」を選択
  3. 「追加」をタップ

#### Scenario: Chrome guide sheet content

- **WHEN** the guide sheet is shown
- **AND** the platform is NOT iOS
- **THEN** the sheet SHALL display:
  1. ブラウザのメニュー（⋮）をタップ
  2. 「ホーム画面に追加」を選択
  3. 「追加」をタップ

#### Scenario: Manual confirm from guide sheet

- **WHEN** the user taps the "追加しました" button in the guide sheet
- **THEN** the system SHALL call `PwaInstallService.confirmInstalled()`
- **AND** the guide sheet SHALL close
- **AND** the banner SHALL be permanently removed

#### Scenario: CTA mode upgrades reactively when deferred prompt arrives

- **WHEN** the banner is visible in guide mode
- **AND** the browser fires `beforeinstallprompt` (deferred prompt arrives)
- **THEN** `PwaInstallService.canShowFab` becomes `true`
- **AND** the banner CTA SHALL reactively switch to native one-tap mode without a page reload

---
