## 1. Restore event-card journey badge

- [x] 1.1 In `src/components/live-highway/event-card.html`, add back the journey badge `<span>` inside the `<article>` element, after the location-label span: `<span if.bind="journeyConfig" data-journey-status.bind="event.journeyStatus" class="journey-badge" data-testid="journey-badge" role="img" aria-label.bind="journeyConfig.labelKey | t">${journeyConfig.icon}</span>`

## 2. Restore event-detail-sheet journey section

- [x] 2.1 In `src/components/live-highway/event-detail-sheet.html`, restore the `<section if.bind="isAuthenticated" class="sheet-journey">` block between the closing `</section>` of `.sheet-details` and the opening `<footer class="sheet-actions">`, containing the full journey radiogroup: process phase (tracking → applied) and outcome phase (unpaid → paid | lost), plus the remove button
- [x] 2.2 Verify the restored section includes: `data-testid="sheet-journey"` on the section, `data-testid="journey-btn"` on each radiogroup button, and `data-testid="journey-remove-btn"` on the remove button

## 3. Verify and ship

- [x] 3.1 Run `make check` in the frontend repo — lint, typecheck, and unit tests must all pass
- [ ] 3.2 Open a PR against `frontend` main with the two template changes
- [ ] 3.3 Merge PR and create a patch release to ship to prod
