## REMOVED Requirements

### Requirement: Long-press gesture triggers unfollow confirmation on touch devices

**Reason**: The hidden 500 ms long-press gesture does not work on iOS Safari — the OS text-selection / callout / magnifier gesture fires `pointercancel` before the timer completes, and because the visible trash column is hidden on `pointer: coarse` devices, long-press is the only unfollow path there, leaving touch users unable to unfollow. Long-press is also a hidden, non-discoverable gesture whose semantics match neither the iOS (system-reserved) nor Android (multi-select) convention. It is superseded by the `edit-mode-unfollow` capability, which is discoverable, single-pointer (WCAG 2.5.1), and works identically across pointer types.

**Migration**: Unfollow from the My Artists list is now performed via the Edit-mode toggle in the page header, which reveals a per-row remove (−) control; tapping it unfollows immediately with an Undo affordance (see the `edit-mode-unfollow` capability). The `ArtistUnfollowSheet` confirmation sheet, the `long-press` custom attribute, and the `pointer: coarse` trash-column hiding are removed. No user data migration is required.
