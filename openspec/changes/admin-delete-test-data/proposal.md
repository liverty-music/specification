## Why

Production holds test data from building the organizer and ticketing flows, and it is now visible or in the way:

- 15 test Organizers, each with its own Zitadel tenant.
- Two PUBLIC test Series for a real artist, both openable as public event pages since `public-event-page` shipped.
- Their media in GCS.
- Test fan accounts.

No interface can remove any of it. Organizers can only be deactivated, and `UserUseCase.Delete` is exposed nowhere. Raw SQL against production would skip the dependent records in GCS and Zitadel, and is easy to get wrong around purchases. An admin-only, checked deletion through the admin API removes the test data and everything that depends on it, and refuses when real money is involved.

## What Changes

- **Admin `OrganizerService.Delete`** permanently removes a **deactivated** Organizer together with:
  - its first-party Series and their Events, with each Event's lottery sales phases, ticket applications, ticket journeys and performer links;
  - the Orders and Tickets for those Events, allowed only when every Order is Refunded;
  - its Media records and the media objects in GCS (originals and served variants);
  - its Zitadel tenant, with the tenant's operators;
  - its artist associations and its payout-account record.
- **Organizer deletion is refused (FailedPrecondition, nothing removed) when:**
  - the Organizer is not deactivated;
  - any of its Events has an Order that is not Refunded;
  - any of its Events has a Settlement;
  - the Organizer has a connected payout account.
- **New admin `UserService.Delete`** permanently removes a fan User: the User with its follows, ticket journeys, notifications, push subscriptions, sales-phase reminders, verified identity and home area, plus its Zitadel user.
  - It is refused (FailedPrecondition) while the User holds an Issued Ticket or an Order that is not Refunded.
  - Its other Orders, Tickets and ticket applications remain, as `User.Delete` already specifies.
- **Retryable:** the GCS objects and the Zitadel tenant or user are removed before the database records, and every removal treats "already gone" as done, so a failed call can simply be repeated.
- **Not covered:**
  - Records in Stripe are kept; Stripe does not allow deleting them.
  - Zitadel users that have no backend User (e.g. accounts that never finished sign-up) are removed in the Zitadel console.
  - No admin console screen is added; the RPCs are called directly by an admin.

## Capabilities

### New Capabilities

- `components/usecase/organizer/delete`: OrganizerUseCase.Delete. It checks that the Organizer is deactivated and that nothing blocks deletion, then removes the media objects, the tenant and the Organizer's records.
- `components/entity/organizer/delete`: Organizer.Delete. It removes, in one transaction, the Organizer with its Series, Events, purchases, Media records and associations, and refuses on any blocker.
- `components/entity/organizer/delete-tenant`: Organizer.DeleteTenant. It removes the Organizer's Zitadel tenant with its operators; a tenant that is already gone counts as done.
- `components/entity/media/list-by-organizer`: Media.ListByOrganizer. It returns every Media record an Organizer owns, so its objects can be removed.
- `components/entity/media/delete-original` and `components/entity/media/delete-variants`: Media.DeleteOriginal and Media.DeleteVariants. They remove a Media's uploaded original and its served variants; a file that is already gone counts as done. These operations already exist (the media pipeline uses them) and get their spec here.
- `components/entity/user/delete-identity`: User.DeleteIdentity. It removes the User's Zitadel user; an identity that is already gone counts as done.
- `components/entity/order/list-by-buyer`: Order.ListByBuyer. It returns the Orders a User bought, so deletion can refuse on one that is not Refunded.
- `components/adapter/admin/api/rpc/user`: the admin UserService boundary. Delete is admin-only, validates the UserId and runs UserUseCase.Delete.

### Modified Capabilities

- `components/adapter/admin/api/rpc/organizer`: adds Delete. Delete is admin-only, requires an OrganizerId and runs OrganizerUseCase.Delete.
- `components/usecase/user/delete`: exposed through the admin UserService. It now also removes the User's Zitadel user, and refuses while the User holds an Issued Ticket or an Order that is not Refunded.

Unchanged, and relied on:

- `components/entity/user/delete`: User.Delete already removes everything the User owns and keeps purchases.
- `components/entity/ticket/list-by-holder`: Ticket.ListByHolder, for the Issued-ticket check.
- `components/entity/user/get` and `components/entity/organizer/get`: they load the User and the Organizer.
- `components/entity/organizer`: deactivated is already a final state in its lifecycle diagram.

## Impact

- **specification:**
  - `rpc/admin/organizer/v1`: `Delete`, with request and response.
  - New `rpc/admin/user/v1` `UserService.Delete`.
  - The change is additive.
- **backend:**
  - New usecases: OrganizerUseCase.Delete and an extended UserUseCase.Delete.
  - New repository operations, each in one transaction: Organizer.Delete, Media.ListByOrganizer and Order.ListByBuyer.
  - Zitadel removal of org and user, through the organizer provisioner's Management API client.
  - GCS deletion through the existing ImageStorer.
  - The admin handlers, registered on the admin server.
- **cloud-provisioning:** none expected. The backend's Zitadel machine user must be allowed to remove orgs and users, and `admin-console-api` needs the media bucket settings; both are verified in tasks 1.1 and 1.2, and anything missing is added in group 7.
- **Operations:** a cleanup run of production test data with these RPCs. The test Organizers are deactivated first, through the existing `Deactivate`.
