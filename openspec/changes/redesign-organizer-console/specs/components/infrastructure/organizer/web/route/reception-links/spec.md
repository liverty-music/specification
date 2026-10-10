# Spec Delta

## REMOVED Requirements

### Requirement: One link per device

**Reason**: The reception links screen becomes the Reception (受付) tab of the event page, so the operator reaches it from the event instead of a separate address.
**Migration**: Specified in `components/infrastructure/organizer/web/route/event` as "The Reception tab lists one Scanner per device", in the Scanner vocabulary of `rename-reception-to-scanner`; the behavior is unchanged.

### Requirement: Revoke and reissue in one step

**Reason**: Moves with the screen into the event page's Reception tab.
**Migration**: Specified in `components/infrastructure/organizer/web/route/event` as "Revoke and reissue a Scanner" and "The Reception tab explains a missing prerequisite"; the confirmation now names the effect on the device.
