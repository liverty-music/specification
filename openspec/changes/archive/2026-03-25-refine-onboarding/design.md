## Context

The current onboarding flow is implemented as a strict linear state machine (LP → DISCOVERY → DASHBOARD → DETAIL → MY_ARTISTS → COMPLETED) with the `OnboardingService` holding a single `onboardingStep` persisted to localStorage. Coach marks use a global `CoachMark` component in the app shell, targeting DOM elements via CSS selector with a blocker-div overlay that intercepts all taps outside the spotlight.

Key pain points driving this redesign:
- `onOnboardingCardTapped()` in `dashboard-route.ts` hijacks the card tap to advance the step instead of opening the Detail Sheet, making the app appear broken
- Lane Intro auto-advances every 2 seconds with scroll locked, giving users no time to explore the timetable
- Hype changes are reverted on the `MY_ARTISTS` step, immediately contradicting the "raise your hype" coaching message
- The `DETAIL` step exists solely to hold a spotlight on the My Artists nav tab — it adds a step with no new screen
- Celebration shows before the lane intro, before the user has any context for what they're celebrating

## Goals / Non-Goals

**Goals:**
- Remove the perception that the app is broken during onboarding
- Maximize time users spend experiencing the timetable (the product's core value)
- Shift guidance from push (forced spotlight sequence) to pull (user-triggered `?` icon)
- Persist guest hype selections through to signup (no silent data loss)
- Introduce `PostSignupDialog` to consolidate notification + PWA prompts at the highest-engagement moment

**Non-Goals:**
- Adding back navigation between onboarding steps
- Tracking detailed analytics of onboarding funnel drop-off (separate concern)
- Backend or proto changes — this is a pure frontend change

## Decisions

### Decision 1: Remove DETAIL step; DASHBOARD completes on Celebration open

The DETAIL step was created to show a My Artists tab spotlight after the card tap. With the new design, the card tap opens the actual Detail Sheet (restoring expected behavior) and the sequential guide ends at Celebration open. The `DASHBOARD` → `MY_ARTISTS` step advance happens when the Celebration overlay opens — not on card tap, not on sheet close.

**Why Celebration open?** It is the last controlled moment before the user enters free exploration. Advancing the step here means the My Artists nav is naturally reachable without any artificial gate.

**Alternative considered**: Advance step on Celebration dismiss. Rejected because the Celebration is the conceptual "you're done with the guided part" moment — the step should reflect that on open, not after the user taps away.

### Decision 2: Lane Intro becomes tap-to-advance; Home Selector inline in HOME phase

Auto-advance (2-second timer) is removed. Each phase waits for a tap. This is architecturally simpler (no timer to clear on interrupt) and ensures users actually read the coach mark text.

The Home Selector bottom-sheet opens during the HOME phase rather than before Lane Intro. This provides the "why" context — users see the HOME STAGE being spotlighted when asked about their居住エリア, making the question self-explanatory. The selected prefecture is then available for dynamic interpolation in the HOME phase coach mark text.

**Alternative considered**: Show Home Selector before Lane Intro starts (current approach). Rejected because it presents a region question with no visual context, leading to confusion.

### Decision 3: PageHelp replaces popover snack and HypeNotificationDialog

A persistent `?` icon in the page header serves three purposes:
1. Replaces the 5-second auto-dismiss popover snack on Discovery
2. Provides on-demand hype explanation on My Artists (replacing `HypeNotificationDialog` auto-popup)
3. Creates a consistent re-entry point for users who dismissed guidance too quickly

Auto-opens once per page per onboarding session. Uses a per-page localStorage flag (`liverty:onboarding:helpSeen:<page>`) to track first-open state.

**Why not coach mark `?` spotlight?** The `?` is the guide entry point itself — spotlighting it with a coach mark would require a coach mark to explain the coach mark. Auto-opening the content directly is cleaner.

### Decision 4: Coach mark `router.load()` removed; nav href delegates navigation

`onTargetClick` in `coach-mark.ts` currently calls both `currentTarget.click()` (which triggers the nav href) and `onTap?.()` (which calls `router.load()`). This double-fires routing. Removing `router.load()` from `onTap` leaves navigation entirely to the nav element's default href behavior. Blocker divs and scroll lock during Lane Intro are unchanged.

### Decision 5: Guest hype persisted to localStorage; merged on signup

`GuestService` gains a `hypes` map (`artistId → HypeType`) stored under `liverty:guest:hypes`. The hype revert logic in `my-artists-route.ts` is removed. On signup, `auth-callback-route.ts` reads `guest.hypes` and calls `FollowService.SetHype` per artist as part of the existing merge sequence.

**Why not wait for signup to set hype?** The user's intent has been expressed — discarding it silently is a trust violation. Persisting and merging mirrors how followed artists are handled.

### Decision 6: PostSignupDialog on auth-callback

After `provisionUser()` completes, `auth-callback-route.ts` navigates to `/dashboard` and sets a one-time flag (`liverty:postSignup:shown`). The dashboard reads this flag on load and shows `PostSignupDialog` if present, then clears it. The dialog surfaces notification opt-in and PWA install prompt in one surface, preventing the `IPromptCoordinator` race between `PwaInstallPrompt` and `NotificationPrompt`.

## Risks / Trade-offs

- **Home Selector inline in HOME phase adds complexity to Lane Intro state machine** → Mitigation: Add a `waiting-for-home` sub-state to `laneIntroPhase`; the HOME phase does not auto-advance until `onHomeSelected` fires.

- **DASHBOARD step completing on Celebration open means users who dismiss Celebration immediately land in free exploration with MY_ARTISTS step active, but no coach mark** → This is intentional and acceptable. The `?` icon on My Artists provides on-demand guidance. No forced spotlight needed.

- **`hasUpcomingEvents` snack retained alongside `?` guide** → Minor duplication risk if both fire simultaneously. Mitigation: `?` guide content is static reference material; snack is event-driven feedback. They serve different purposes and do not conflict.

- **Welcome page live data fallback** → If all artists in the fallback list have zero concerts, the preview renders an empty state. Mitigation: fallback list is kept large (10–15 artists); the empty state is styled as "coming soon" rather than an error.

## Migration Plan

1. Remove `OnboardingStep.DETAIL` from `onboarding.ts` and update `STEP_ROUTE_MAP`
2. Update `onboarding-service.ts` step ordering; existing localStorage values of `'detail'` should fall back to `'dashboard'` on read
3. Update `dashboard-route.ts`: remove DETAIL step logic, fix card tap to open Detail Sheet, change Celebration to trigger DASHBOARD→MY_ARTISTS step advance on open, make Lane Intro tap-to-advance, inline Home Selector in HOME phase
4. Update `coach-mark.ts`: remove `router.load()` from `onTargetClick`
5. Update `discovery-route.ts`: replace popover snack with PageHelp auto-open, update coach mark to 2-second fade
6. Update `my-artists-route.ts`: remove revert logic, remove HypeNotificationDialog show logic, add PageHelp auto-open
7. Create `PageHelp` component
8. Update `GuestService`: add hype storage; update `auth-callback-route.ts` merge to include hypes
9. Create `PostSignupDialog` component; wire into auth-callback + dashboard
10. Update `welcome-route.ts`: embed dashboard preview with fallback artist list

No backend changes. No proto changes. Rollback: revert frontend changes; localStorage `liverty:onboardingStep` values are forward-compatible (unknown step values default to nearest valid step).

## Flow Diagram

### Step Sequence (Before → After)

```
Before: LP → DISCOVERY → DASHBOARD → DETAIL → MY_ARTISTS → COMPLETED
After:  LP → DISCOVERY → DASHBOARD →          MY_ARTISTS → COMPLETED
```

### Full Onboarding Flow

```
WELCOME (/welcome)
│  Embedded live dashboard preview (read-only, popular artists)
│  "アカウント不要でお試しいただけます"
│  [使ってみる]  [ログイン]
│
│ "使ってみる" tap → clear guest data, set step = DISCOVERY
▼
─────────────────────────────────────────────────────────────
DISCOVERY (/discovery)                                   [?]
─────────────────────────────────────────────────────────────
│  Bubble UI (Matter.js)
│  First visit: PageHelp bottom-sheet auto-opens
│
│  Per follow: hasUpcomingEvents snack (retained)
│
│  Condition met (5 follows OR 3 with concerts):
│    → Coach mark spotlight on Home nav [2s then fade]
│    → User taps Home nav at own pace
│
▼  step = DASHBOARD
─────────────────────────────────────────────────────────────
DASHBOARD (/dashboard) — GUIDED PHASE                    [?]
─────────────────────────────────────────────────────────────
│
│  Lane Intro  [tap-to-advance; blocker divs + scroll lock ON]
│  ┌─ Phase: home ───────────────────────────────────────────┐
│  │  Spotlight [data-stage="home"]                          │
│  │  Home Selector bottom-sheet opens inline                │
│  │  Coach mark: "居住エリアのライブが並びます。             │
│  │               居住エリアはどこですか？"                  │
│  │  → User selects 居住エリア                              │
│  │  → Coach mark updates: "{{prefecture}}のライブ"         │
│  │  → Tap to advance                                       │
│  └─────────────────────────────────────────────────────────┘
│  ┌─ Phase: near ───────────────────────────────────────────┐
│  │  Spotlight [data-stage="near"]                          │
│  │  Coach mark: "少し足を伸ばせば行けるライブ"              │
│  │  → Tap to advance                                       │
│  └─────────────────────────────────────────────────────────┘
│  ┌─ Phase: away ───────────────────────────────────────────┐
│  │  Spotlight [data-stage="away"]                          │
│  │  Coach mark: "遠征ライブ！"                              │
│  │  → Tap to advance                                       │
│  └─────────────────────────────────────────────────────────┘
│
│  Celebration Overlay opens
│    → onboardingStep advances to MY_ARTISTS (on open)
│    "あなただけのタイムテーブルが完成しました！"
│    "自由にタイムテーブルを触ってみよう"
│    → User taps anywhere to dismiss
│
▼  Celebration dismissed
─────────────────────────────────────────────────────────────
DASHBOARD (/dashboard) — FREE EXPLORATION                [?]
─────────────────────────────────────────────────────────────
│  Blocker divs OFF / scroll lock OFF / all nav tabs enabled
│  User browses timetable freely
│
│  Card tap → EventDetailSheet opens (real, interactable)
│             Sheet close → continue browsing freely
│
│  User taps [My Artists] nav at own pace
▼
─────────────────────────────────────────────────────────────
MY_ARTISTS (/my-artists)                                 [?]
─────────────────────────────────────────────────────────────
│  First visit: PageHelp bottom-sheet auto-opens
│    👀 Watch   — 通知なし
│    🔥 Home    — 居住エリアのライブを通知
│    🔥🔥 Nearby — 近くのライブも通知
│    🔥🔥🔥 Away  — 全国のライブを通知
│
│  User changes any hype level
│    → Change persisted (no revert)
│    → Guest: saved to localStorage (liverty:guest:hypes)
│    → Guest: non-modal signup banner shown
│    → step = COMPLETED
▼
─────────────────────────────────────────────────────────────
COMPLETED
─────────────────────────────────────────────────────────────
│  Full app unlocked
│
│  [If arriving via auth-callback after first signup]
│  PostSignupDialog shown on /dashboard:
│    ✅ アカウント登録完了！
│    🔔 新着ライブ通知をオンにしよう  [通知をオンにする]
│    📱 ホーム画面に追加するとより快適に  [ホーム画面に追加]
│                                         [あとで]
```

### Component Behavior Changes

| Component | Before | After |
|-----------|--------|-------|
| `coach-mark` | `router.load()` in `onTargetClick` | Removed; nav href delegates routing |
| `celebration-overlay` | Auto-dismiss (2.5s timer); shown before Lane Intro | Tap-to-dismiss; shown after Lane Intro; advances step on open |
| `dashboard-route` Lane Intro | Auto-advance (2s timer); card spotlight phase | Tap-to-advance; no card phase; Home Selector inline in HOME |
| `dashboard-route` card tap | Hijacked → step advance + My Artists spotlight | Opens `EventDetailSheet` |
| `discovery-route` progression | 3 artists with concerts | 5 follows OR 3 with concerts; coach mark fades after 2s |
| `my-artists-route` hype | Reverted + `HypeNotificationDialog` | Persisted; `PageHelp` auto-open |
| `GuestService` | follows + region | + hype map |

## Open Questions

- Should the Welcome page dashboard preview use a dedicated read-only mode flag to prevent accidental follow actions, or is the absence of auth sufficient?
- Should `liverty:onboarding:helpSeen:<page>` be cleared when onboarding resets (fresh tutorial start)?
