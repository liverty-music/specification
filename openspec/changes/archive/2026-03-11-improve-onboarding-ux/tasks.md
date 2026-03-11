## 1. Coach Mark Visual Overhaul

- [x] 1.1 Update coach-mark.css: overlay opacity from 60% to 75%, tooltip font-size to 16px, padding to 16px, brand accent background, border-radius 12px
- [x] 1.2 Add spotlight pulse ring animation: 2px solid brand-accent border with `@keyframes coach-pulse` (scale 1→1.05→1, 1.5s infinite) on `.coach-mark-spotlight`
- [x] 1.3 Add `prefers-reduced-motion: reduce` media query to disable pulse animation, keep static ring
- [x] 1.4 Implement scroll lock: when coach mark is active, add `overflow: hidden` to `<au-viewport>`; restore on deactivation

## 2. Nav Bar Visibility

- [x] 2.1 Update `showNav` condition in `my-app.ts` to show nav bar on all routes except Landing Page and Auth Callback
- [x] 2.2 Add `data-nav-dashboard` attribute to Dashboard tab link in `bottom-nav-bar.html`
- [x] 2.3 Verify existing route guards (`AuthHook.canLoad()`) correctly prevent navigation during onboarding Steps 1-6

## 3. Event Detail Sheet — Popover Conversion

- [x] 3.1 Replace `<dialog>` with `<div popover="manual">` in `event-detail-sheet.html`; add `role="dialog"` and `aria-modal="true"`
- [x] 3.2 Replace `showModal()` / `close()` calls with `showPopover()` / `hidePopover()` in `event-detail-sheet.ts`
- [x] 3.3 Remove `cancel.trigger="$event.preventDefault()"` handler (not applicable to popovers)
- [x] 3.4 Retain `history.pushState` / `popstate` URL management and swipe-to-dismiss gesture
- [x] 3.5 Implement dismiss blocking during onboarding Step 4 (prevent swipe-down and outside tap)
- [x] 3.6 Verify coach mark for Step 4 (`[data-nav-my-artists]`) renders above the detail sheet in top layer

## 4. Dashboard Layout — Festival Timetable

- [x] 4.1 Change grid from `grid-cols-[50%_30%_20%]` to `grid-cols-3` (equal 1fr 1fr 1fr) in `live-highway.html`
- [x] 4.2 Create sticky STAGE header row: `position: sticky; top: 0` with opaque background, displaying "HOME STAGE / NEAR STAGE / AWAY STAGE" in bold uppercase 14-16px
- [x] 4.3 Remove "Live Highway" title and old `text-[10px]` header labels
- [x] 4.4 Add `container-type: inline-size` to each lane cell
- [x] 4.5 Implement dynamic artist name font sizing with `clamp(12px, 5cqi, 24px)` and `overflow-wrap: break-word`
- [x] 4.6 Remove fixed card heights; allow cards to expand based on content/line breaks

## 5. Hype Visualization — Border + Glow + Neon

- [x] 5.1 Define CSS custom properties for hype tiers (WATCH, HOME, NEARBY, AWAY) using artist color variable
- [x] 5.2 Implement border styles: 1px white/10 (WATCH), 1px artistColor/40 (HOME), 2px artistColor (NEARBY), 2px animated gradient (AWAY)
- [x] 5.3 Implement box-shadow glow: none (WATCH), 8px/30% (HOME), 16px/50% pulse (NEARBY), 24px+48px layered pulse (AWAY)
- [x] 5.4 Implement text-shadow neon: none (WATCH), 4px subtle (HOME), 8px vivid (NEARBY), 12px+24px strong (AWAY)
- [x] 5.5 Create `@keyframes hype-glow-pulse` for NEARBY (2s) and AWAY (1.5s) tiers
- [x] 5.6 Create animated gradient border for AWAY using `@property` or `border-image: conic-gradient` with rotation keyframe
- [x] 5.7 Add `prefers-reduced-motion: reduce` fallback: static styles only, no pulse/rotation
- [x] 5.8 Remove emoji badge elements and `HYPE_META` icon references from `event-card.html` and `event-card.ts`
- [x] 5.9 Pass hype level to event card component; bind CSS classes based on tier

## 6. Step 1 CTA — Nav Bar Dashboard Spotlight

- [x] 6.1 Add observable `concertSearchStatus` map to `discover-page.ts` tracking per-artist search completion (pending/done)
- [x] 6.2 Update `follow()` handler to register search status as `pending` and listen for `SearchNewConcerts` completion or 15s timeout
- [x] 6.3 Compute `showDashboardCoachMark`: true when `followedCount >= 3` AND all followed artists have `done` status
- [x] 6.4 Remove "Generate Dashboard" CTA button (`complete-button-wrapper`) from `discover-page.html`
- [x] 6.5 Add coach mark in discover-page.html targeting `[data-nav-dashboard]` with message "タイムテーブルを見てみよう！"
- [x] 6.6 Handle coach mark tap: `onboarding.setStep(DASHBOARD)`, navigate to `/dashboard`
- [x] 6.7 Replace numeric progress counter with continuous progress bar showing `completedSearchCount / followedCount`

## 7. Celebration Overlay

- [x] 7.1 Create `celebration-overlay` component (ts + html + css) with centered text and confetti particle CSS animation
- [x] 7.2 Implement 2.5s display duration with 400ms fade-out transition
- [x] 7.3 Add one-time flag to prevent replay on page reload (session-scoped, not localStorage)
- [x] 7.4 Wire celebration into dashboard route: show when `onboarding.currentStep === DASHBOARD` on first load
- [x] 7.5 After fade-out, proceed to region selection (if needed) or lane introduction
- [x] 7.6 Add `prefers-reduced-motion` support: skip confetti, 1.5s text display, instant disappear

## 8. Dashboard Lane Introduction Sequence

- [x] 8.1 Add local `laneIntroPhase` state to dashboard component: `'home' | 'near' | 'away' | 'card' | 'done'`
- [x] 8.2 After celebration + region selection, start lane intro: spotlight HOME STAGE header with "地元のライブ情報！"
- [x] 8.3 Auto-advance each phase after 2s timeout or on user tap
- [x] 8.4 Sequence: HOME → NEAR ("近くのエリアのライブも！") → AWAY ("全国のライブ情報もチェック！") → card spotlight
- [x] 8.5 Ensure scroll lock remains active through entire lane intro + card spotlight sequence

## 9. Step 3-4 Coach Mark Messages & Flow

- [x] 9.1 Update Step 3 card coach mark message to "タップして詳細を見てみよう！"
- [x] 9.2 Update Step 4 coach mark message to "アーティスト一覧も見てみよう！"
- [x] 9.3 Ensure Step 4 coach mark activates after detail sheet opens (popover ordering: sheet first, coach mark second)

## 10. i18n Keys

- [x] 10.1 Add/update i18n keys: `discovery.coachMark.viewTimetable` ("タイムテーブルを見てみよう！")
- [x] 10.2 Add i18n key: `dashboard.celebration.complete` ("あなただけのタイムテーブルが完成しました！")
- [x] 10.3 Add i18n keys: `dashboard.laneIntro.home` ("地元のライブ情報！"), `dashboard.laneIntro.near` ("近くのエリアのライブも！"), `dashboard.laneIntro.away` ("全国のライブ情報もチェック！")
- [x] 10.4 Update i18n key: `dashboard.coachMark.tapCard` ("タップして詳細を見てみよう！")
- [x] 10.5 Update i18n key: `dashboard.coachMark.customizeNotifications` → `dashboard.coachMark.viewArtists` ("アーティスト一覧も見てみよう！")
- [x] 10.6 Add i18n key for STAGE headers: `dashboard.lane.home` ("HOME STAGE"), `dashboard.lane.near` ("NEAR STAGE"), `dashboard.lane.away` ("AWAY STAGE")
