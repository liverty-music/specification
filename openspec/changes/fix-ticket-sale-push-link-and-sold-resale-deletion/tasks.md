## 1. Backend (specs: notification "Ticket sale push for a discovered concert", "Ticket sale push for a first-party concert")

- [ ] 1.1 Make `Notification.link` send ticket_sale_announcement and sales_reminder to `/concerts/<id>` for a first-party Series and to `/timetable?concert=<id>` otherwise. Verify with the tests for both scenarios and the updated copy table.
- [ ] 1.2 After the merge and the release, check that the new backend image is rolled out in production (read-only). A real push is not sent.

## 2. Backend (specs: send-resale-sold "Listing's user deleted", delete "User with a resold listing awaiting its refund", list-deletion-blockers "Resold listing awaiting its refund")

- [ ] 2.1 Make `SendResaleSold` return without an email when the listing's User no longer exists. Verify with the test for "Listing's user deleted".
- [ ] 2.2 Make `UserRepository.SerializeDeletion` run `fn` on the lock's connection and commit it. Verify with the pool-of-one test.
- [ ] 2.3 After the merge and the release, check that the new backend image is rolled out and the logs show no new errors (read-only).
