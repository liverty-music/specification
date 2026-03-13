## Context

The current onboarding Step 5 uses a bottom sheet selector for passion levels, requiring 2 taps to change. The coachmark text ("好きなレベルを設定してみよう！") fails to communicate what hype does. Step 6 forces a non-dismissible signup modal. Users reach Step 5 after: Landing → Discovery → Dashboard → Concert Detail → My Artists. By this point, onboarding fatigue is high — the UX must be fast and self-explanatory.

The frontend is Aurelia 2 with CUBE CSS methodology. Onboarding state is managed via `liverty:onboardingStep` in localStorage. Guest follows are stored in localStorage and synced to backend after signup.

## Goals / Non-Goals

**Goals:**
- 1-tap hype changes directly in the artist list (no bottom sheet)
- Communicate hype-notification linkage at the moment of highest user motivation
- Provide signup opt-out ("あとで") while maintaining persistent signup CTAs
- Eliminate localStorage hype state for unauthenticated users (avoid sync bugs)
- Complete onboarding in fewer mandatory steps

**Non-Goals:**
- Changing the hype proto schema (HYPE_TYPE values remain unchanged)
- Modifying notification delivery logic
- Redesigning the Grid (Festival) view (list view only)
- Implementing the NEARBY tier in backend notification filtering (remains Phase 2)

## Decisions

### Decision 1: Inline dot slider instead of bottom sheet

**Choice**: 4-stop discrete slider on each artist row, aligned with sticky header columns.

**Why**: Bottom sheet requires 2 taps, interrupts scanning flow, and provides no spatial context for what levels mean. An inline slider enables 1-tap changes and the sticky header provides persistent context.

**Alternative considered**: Segmented control per row — rejected because segments with emoji labels (👀🔥🔥🔥🔥🔥🔥🔥🔥🔥) consume too much horizontal space and look cluttered.

**Implementation**:
- Sticky header: `position: sticky; top: 0` with `backdrop-filter: blur(8px)` on `surface-raised` background
- Header uses CSS Grid with 4 equal columns aligned to slider stop positions
- Each artist row: `display: flex` with artist name (`flex-shrink: 1; overflow: hidden; text-overflow: ellipsis`) and slider (`flex-grow: 1`)
- Slider: 4 dot stops connected by a 2px track line; active dot is 14px with artist-color glow matching hype tier CSS effects from `passion-level` spec
- Tap target: each dot has a 44×44px transparent hit area (minimum touch target per WCAG)
- Slider change emits a custom event; for authenticated users, calls `SetHype` RPC with optimistic update

### Decision 2: Block hype changes for unauthenticated users

**Choice**: Slider tap triggers the notification dialog instead of changing hype. The slider does not move.

**Why**: Allowing hype changes before signup would require persisting hype values in localStorage per artist per follow, then syncing them to backend after signup. The current guest data merge already handles follow list sync — adding hype sync increases complexity and bug surface (race conditions, partial sync, stale state).

**Alternative considered**: Allow changes with localStorage persistence — rejected due to sync complexity. The follow sync (ListFollowed → diff → bulk SetHype) would need to handle: (a) artists unfollowed before signup, (b) hype values changed multiple times, (c) concurrent follow/unfollow during sync.

**Implementation**:
- `HypeSlider` component checks `AuthService.isAuthenticated` on tap
- If unauthenticated: dispatch `hype-signup-prompt` event (caught by parent page)
- If authenticated: update hype optimistically and fire RPC
- All sliders show at WATCH position for unauthenticated users (this is the truth — they have no hype set)

### Decision 3: Coachmark targets sticky header, not individual artist

**Choice**: Spotlight the entire sticky header legend row.

**Why**: The header contains the visual language (emoji + labels) that gives meaning to the slider stops. Spotlighting it teaches users to read the legend, which persists during scroll. Spotlighting an individual artist's slider doesn't explain what the stops mean.

**Implementation**:
- Coach mark target: `[data-hype-header]` attribute on the sticky header element
- Coach mark message: "絶対に見逃したくないアーティストの熱量を上げておこう"
- Dismiss: tap anywhere on overlay (standard coach mark behavior)
- After dismiss: `onboardingStep` advances to 7 (COMPLETED) — onboarding is done
- No more Step 6 (forced signup modal is removed)

### Decision 4: Single-page notification dialog on first unauthenticated slider tap

**Choice**: One dialog explaining hype tiers → notification scope, with signup CTA and "あとで" option.

**Why**: 3-page slide carousel was considered but rejected — users are at Step 5 with high onboarding fatigue. A single page with clear mapping (hype tier → notification scope) is sufficient. The dialog triggers at peak motivation (user just tried to change something).

**Dialog content**:
```
🔔 ライブ通知について

👀 通知なし
🔥 地元のライブを通知
🔥🔥 近くのライブも通知
🔥🔥🔥 全国のライブを通知

通知を受け取るにはアカウント登録が必要です

[ アカウント作成 ]    ← primary button
[ あとで ]            ← ghost button
```

**Trigger condition**: First slider tap while unauthenticated AND `onboardingStep >= 5` (onboarding completed or in progress). The "shown" state is tracked in the existing `onboardingStep` progression — once the user reaches Step 7, the dialog has been shown or is no longer relevant for onboarding.

**"アカウント作成" flow**: Initiates Zitadel OIDC Passkey flow (same as current Step 6).
**"あとで" flow**: Closes dialog, does not change slider, shows inline banner.

### Decision 5: Persistent inline signup banner

**Choice**: A compact banner at the bottom of the artist list (scroll content, not sticky) and at the bottom of the dashboard lane area.

**Why**: After dismissing the dialog, users need a non-intrusive path back to signup. Inline placement (not sticky) avoids obscuring content. Two locations (My Artists + Dashboard) ensure the CTA is visible on the two most-visited pages.

**Implementation**:
- Shared `signup-prompt-banner` component used in both pages
- Conditionally rendered: `!authService.isAuthenticated`
- My Artists: placed after the last artist row in the scroll container
- Dashboard: placed after the lane grid in the scroll container
- Copy: "🔔 通知を有効にするには [アカウント作成]"
- On signup completion: component's `isAuthenticated` binding triggers removal

### Decision 6: Default hype changes from HOME to WATCH

**Choice**: New follows default to WATCH (HYPE_TYPE_WATCH).

**Why**: Starting at WATCH means users experience "raising" hype — a positive action. Starting at HOME means users would need to "lower" it, which feels like removing something. WATCH also means zero notifications by default, which is a safer UX for users who haven't explicitly opted in.

**Backend change**: `FollowArtist` handler sets default hype to `HYPE_TYPE_WATCH` instead of `HYPE_TYPE_HOME`. This is a behavior change, not a schema change.

**Migration**: Existing users' hype values are unchanged. Only new follows after deployment get the new default.

### Decision 7: Emotion-based tier labels

**Choice**: Japanese UI labels use emotion-based phrasing; internal proto values unchanged.

| Proto Value | Current UI Label | New UI Label (ja) | New UI Label (en) |
|-------------|------------------|--------------------|---------------------|
| WATCH | Watch / 👀 | チェック | Just checking |
| HOME | Home / 🔥 | 地元 | Local shows |
| NEARBY | NearBy / 🔥🔥 | 近くも | Nearby too |
| AWAY | Away / 🔥🔥🔥 | どこでも！ | Anywhere! |

**Why**: "Watch/Home/NearBy/Away" are proximity concepts that make sense to developers but not to users asking "how much do I care about this artist?" Emotion-based labels map to user intent.

## Risks / Trade-offs

**[Risk] Users skip signup entirely** → Mitigation: Inline banner provides persistent, non-intrusive CTA on both primary pages. The hype slider being locked at WATCH creates functional motivation to sign up (they can see the slider but can't use it). Future: consider time-delayed re-prompt after N sessions.

**[Risk] Coachmark on header doesn't draw attention to sliders** → Mitigation: The coachmark copy mentions "熱量を上げておこう" which creates curiosity to try the sliders. The header spotlight with emoji labels is visually distinct. If conversion is low, can add a secondary coachmark on the first artist's slider.

**[Risk] Default WATCH breaks existing user expectations** → Mitigation: Only affects NEW follows after deployment. Existing follows retain their current hype. The "raise to enable" pattern is standard in notification UX (iOS, Android both default to off).

**[Risk] Disabled sliders frustrate unauthenticated users** → Mitigation: Sliders are visually at WATCH (not greyed out/disabled). They respond to tap with the notification dialog, which explains why and provides a clear path. This is a "gate" not a "wall" — the path forward is obvious.
