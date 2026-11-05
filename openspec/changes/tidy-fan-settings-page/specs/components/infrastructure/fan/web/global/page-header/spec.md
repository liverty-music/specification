# Spec Delta

## REMOVED Requirements

### Requirement: Page header offers a Settings entry on tab pages

**Reason**: The gear sat at the top-right corner, out of thumb reach. Settings is now the last item of the FAB launcher on the four tab pages (`components/infrastructure/fan/web/global/fab-menu` "The launcher ends with Settings on the tab pages"), and one entry is kept so fans learn one place.
**Migration**: Fans open Settings from the FAB launcher. Tests that open Settings through the header gear open it through the launcher instead.
