## Why

The organizer console remembered an Organization on the device as soon as an address named it (`?org=` or `?org_id=`), before any sign-in. A link to an Organizer that does not exist, or no longer does, therefore stuck to the device: every later visit started the same failing sign-in and never showed the find-organizer screen (frontend#1076). The hosted-login spec already says the console remembers the Organization "after a sign-in", but no scenario covers a link whose sign-in fails, so nothing guarded against the bug.

## What Changes

- An Organization is remembered on the device only after a sign-in to it admits the member; only then does it replace the Organization remembered before.
- An Organization named only by an address whose sign-in did not admit the member is not remembered and does not replace the remembered one. The next visit without the address signs in to the remembered Organization, or shows the find-organizer screen when none is remembered.
- The implementation shipped before this change: frontend#1079, released in frontend v1.171.0. This change records the guarantee in the spec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/organizer/web/global/hosted-login`: "Every console sign-in names one Organization" states that only an Organization a sign-in admitted the member to is remembered, and gains the scenarios "Link to an Organizer that does not exist" and "Failed link keeps the remembered Organization".

Unchanged: `components/infrastructure/organizer/web/route/find-organizer` ("A sign-in link opens the console for its Organizer") already remembers the Organization after the owner signs in, and `components/infrastructure/organizer/web/global/organizer-shell` ("Without a known Organization the console asks for the email") already describes the find-organizer screen the failed link now leads to.

## Impact

- frontend: organizer console bootstrap (`organizer/services/org-handle.ts`) and route guard (`organizer/hooks/auth-hook.ts`). Already merged (frontend#1079); only test annotations for the new scenarios remain.
- No proto, backend or infrastructure change.
