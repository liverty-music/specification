## 1. Backend: Add ListWithProximity to public whitelist

- [x] 1.1 Add `"/" + concertconnect.ConcertServiceName + "/ListWithProximity": true` to `publicProcedures` map in `backend/internal/di/provider.go`
- [x] 1.2 Verify existing auth interceptor test covers public procedure bypass, add test case for ListWithProximity if missing

## 2. Frontend: Fix My Artists coach mark dismissal

- [x] 2.1 In `frontend/src/routes/my-artists/my-artists-route.ts`, add `onTap` callback to `activateSpotlight` that calls `this.onboarding.deactivateSpotlight()`
- [ ] 2.2 Manually verify on dev: tap hype header spotlight → spotlight dismisses → hype slider is interactive → onboarding completes (post-deploy)

## 3. Frontend: Update BSR package

- [x] 3.1 Run `npm install` in `frontend/` to resolve latest BSR package version matching semver range
- [x] 3.2 Verify `TicketJourneyService.listByUser` exists in the updated `node_modules/@buf/liverty-music_schema.connectrpc_es` JS file
- [ ] 3.3 Commit updated `package-lock.json` (pending commit)

## 4. Frontend: Fix bottom-sheet scroll-area height in popover top-layer

- [x] 4.1 In `frontend/src/components/bottom-sheet/bottom-sheet.css`, change `.scroll-area { block-size: 100% }` to `block-size: 100dvh`
- [x] 4.2 Update bottom-sheet-ce spec to document `100dvh` sizing requirement
- [x] 4.3 Run `make check` in frontend

## 5. Verification

- [x] 5.1 Run `make check` in backend
- [x] 5.2 Run `make check` in frontend
- [ ] 5.3 Deploy to dev and run full onboarding flow end-to-end: discovery → dashboard (lane intro with concert data) → my-artists (spotlight tap → hype slider → complete)
