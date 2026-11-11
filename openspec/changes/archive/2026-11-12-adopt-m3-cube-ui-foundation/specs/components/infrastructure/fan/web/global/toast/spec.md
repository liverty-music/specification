## REMOVED Requirements

### Requirement: Toast custom element as a top-positioned popover banner
**Reason**: No screen renders `<toast>`. Its last user, the PWA install prompt, became the bottom `pwa-install-banner` in 2026-04, and transient messages use the snack bar. Material 3 defines no toast: its components for messages are the snackbar (low priority, optional action) and the dialog (high priority, required action).
**Migration**: Transient status messages use `<snack-bar>` (`snack-bar`); a prompt that needs the fan's action uses a bottom banner, a dialog or a bottom sheet.
