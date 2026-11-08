# Tasks

## 1. Frontend: Discovery route (components/infrastructure/fan/web/route/discovery)

- [ ] 1.1 In `src/routes/discovery/discovery-route.ts`, start the reveal timing of a cold visit only when the page is not hidden at `loading()`, and drop it in the hidden branch of `onVisibilityChange`; verify with tests in `test/routes/discovery-route.spec.ts` annotated `@spec components/infrastructure/fan/web/route/discovery "Page hidden before the reveal completes"`, one for a page hidden when Discovery opens and one for a page hidden during the reveal, each asserting no `perf.discovery_reveal` is captured after the page is shown again and every name is drawn, and verify the existing reveal-timing tests still pass
- [ ] 1.2 Run a cold load of Discovery as a guest in a local production build with Playwright, with analytics on and the page visible throughout, and verify one `perf.discovery_reveal` is still captured (the visible path is unchanged)
