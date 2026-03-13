## Why

The current onboarding Step 5 (My Artists) uses a 2-tap passion level selector (tap icon → bottom sheet → select) with a coachmark that says "好きなレベルを設定してみよう！" — neither the UI nor the text communicates what hype levels actually do. Users don't understand the connection between hype and notification scope, and the friction of a bottom sheet discourages exploration. Additionally, the current flow forces a non-dismissible signup modal (Step 6) with no opt-out, losing users who aren't ready to commit.

## What Changes

- **Replace bottom sheet selector with inline dot slider**: Each artist row gets a 4-stop slider (WATCH/HOME/NEARBY/AWAY) enabling 1-tap hype changes directly in the list view
- **Add sticky header with hype level legend**: Visual column headers (👀/🔥/🔥🔥/🔥🔥🔥 with labels) that remain visible during scroll, aligning with slider stop positions
- **Change default hype from HOME to WATCH**: New follows start at WATCH (👀) so users experience "raising" hype (positive) rather than "lowering" it
- **Redesign Step 5 coachmark**: Spotlight the sticky header legend instead of an individual artist's hype icon, with motivation-focused copy ("絶対に見逃したくないアーティストの熱量を上げておこう")
- **Replace Step 5→6 explanation dialog with notification-focused dialog**: On first slider change, show a single-page dialog explaining hype-notification linkage and presenting signup CTA with "あとで" opt-out
- **Block hype changes for unauthenticated users**: Slider tap triggers the notification dialog; the slider does not move until after signup (no localStorage hype state to sync)
- **Add inline signup banner to My Artists and Dashboard**: After dismissing the dialog with "あとで", show a persistent inline banner prompting account creation; banner disappears after signup
- **Replace non-dismissible Step 6 signup modal**: The signup prompt is now integrated into the hype dialog and inline banner; the forced modal is removed
- **Update hype tier labels**: Use emotion-based labels (チェック/地元/近くも/どこでも！) instead of functional labels (Watch/Home/NearBy/Away)
- **Apply hype-level CSS effects to slider active dot**: The selected dot mirrors the dashboard card glow for that tier, making the slider itself a preview

## Capabilities

### New Capabilities

- `hype-inline-slider`: Inline 4-stop dot slider for setting hype level per artist in the My Artists list view, with sticky header legend and artist-color glow on active dot
- `signup-prompt-banner`: Persistent inline banner on My Artists and Dashboard pages prompting unauthenticated users to create an account, dismissed on signup completion

### Modified Capabilities

- `my-artists`: Replace bottom sheet passion selector with inline dot slider UI; artist row layout changes from name + icon to name + slider on same row
- `onboarding-tutorial`: Step 5 coachmark targets header legend instead of individual artist icon; Step 5 slider interaction triggers notification dialog instead of passion explanation; Step 6 non-dismissible signup modal replaced by dialog CTA and inline banner flow
- `passion-level`: Default hype changes from HOME to WATCH; add emotion-based tier labels for UI display; hype changes blocked for unauthenticated users (no localStorage hype persistence)
- `frontend-onboarding-flow`: Remove forced signup modal at Step 6; onboarding completes at Step 5 coachmark dismissal; signup is prompted via hype dialog and inline banner

## Impact

- **Frontend (My Artists page)**: Complete redesign of artist list row layout and hype interaction pattern
- **Frontend (Dashboard)**: Add inline signup banner component
- **Frontend (Onboarding service)**: Step 5/6 logic rewrite; Step 6 modal removal; new dialog and banner components
- **Backend (Follow service)**: Default hype value changes from HOME to WATCH for new follows
- **Proto (follow.proto)**: No schema changes needed (WATCH already exists as HYPE_TYPE_WATCH)
- **Specification**: Multiple capability specs updated
