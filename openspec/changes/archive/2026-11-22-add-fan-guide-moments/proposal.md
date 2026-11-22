## Why

The fan web has grown features that fans do not find: following by tapping a bubble, the Concerts view behind an icon-only swap tile, the area and period filter behind the action menu, the 🔔 ticket sale notification and the 🔥 hype dots. Almost no fan opens help, and the help that opens on its own during onboarding reads like a manual. Walking real first sessions through the code also showed that the flow itself confuses fans: a guest's 🔔 press jumps straight to the hosted sign-up page with no word of why, a sign-up started from 🔔 comes back to a celebration and a notification step about new concerts instead of the concert the fan asked about, a guest is asked for an area twice (Concerts view, then Timetable), and the same place is called ホームエリア, 居住エリア and HOMEエリア.

## What Changes

- Add **guide moments**: one short line in the app's friend voice next to a glowing control, with no dimmed screen and no steps. Five moments, each shown once per device at the moment the fan needs it:
  - Discovery, artist bubbles, a fan who follows no artist: 「気になるアーティストをタップしてフォローしよう！」 on the bubble field.
  - Discovery, a signed-in fan whose onboarding is complete, first time on the artist bubbles: 「すぐに行けるライブも見てみよう！」 on the swap tile.
  - Discovery, the Concerts view, first time its list or empty state shows: 「遠征するときはココを変更！」 on the action menu.
  - Concert sheet, a concert the fan has no status for, for a fan with no journey at all, not on Welcome: 「気になるライブは見逃しNG！」 above the 🔔 button.
  - My Artists, no followed artist moved off the default hype level, guests included: 「Hype（熱量）に合わせて 🔥 を変えてみよう！」 on the 🔥 dots.
- One guide moment at a time, none while a sheet, dialog or celebration is up; a moment blocked that way shows once after the blocker closes. Seen marks stay on the device through sign-up and sign-in. Help gets a 「チュートリアル」 button that replays the moment of its section.
- **BREAKING (behavior)**: help no longer opens on its own on a first visit to Discovery or My Artists; the guide moments replace it.
- Guests no longer see the swap tile or the Concerts view: Discovery's Concerts address opens the artist bubbles for a guest, and the Timetable's empty state offers 「ライブを探す」 only to signed-in fans. The Concerts view's area override is then a signed-in fan's choice only.
- A guest's 🔔 press opens a dialog first: 「おっと、まだアカウントを持っていないね？」 / 「通知に必要なアカウントは無料ですぐに作成できるよ！」 with 「あとで」 and 「Sign Up」. The always-shown guest line in the ticket section goes away.
- Welcome's demo concert sheet shows no 🔔 button and no push line.
- A sign-up started from 🔔 returns to the concert sheet with no confetti celebration; the post-signup dialog opens when the fan closes the sheet, its notification step titled 「あとはプッシュ通知をオンにするだけ！」 with no body.
- The concert sheet's follow action moves next to the artist name and reads 「Follow」 / 「Following」.
- Copy: 「Sign Up」 replaces 「登録する」 for sign-up actions; HOMEエリア is the one name for the home area in the UI; the guest signup banner reads 「新着ライブ通知を受け取ろう！」; the post-signup celebration's second line reads 「新着ライブは / Liverty Music にお任せ！」; the Concerts view's filter item reads 「エリアと期間を変える」; the home-area sheet asks 「住んでるエリアを教えてね！近くのライブを HOME に並べるよ」.

## Capabilities

### New Capabilities
- `components/infrastructure/fan/web/global/guide-moment`: the guide moment surface — how one moment looks, when it may show, when it ends, how it is remembered, replayed and reported.

### Modified Capabilities
- `components/infrastructure/fan/web/route/discovery`: the bubble-field and swap-tile moments; guests see no swap tile or Concerts view; the onboarding guidance no longer opens help; the Concerts view's moment, filter item label and area override for signed-in fans only.
- `components/infrastructure/fan/web/route/my-artists`: the hype moment; the hype snack's 「Sign Up」 action and HOMEエリア place word.
- `components/infrastructure/fan/web/route/timetable`: the empty state's Concerts view link for signed-in fans only.
- `components/infrastructure/fan/web/route/welcome`: the demo concert sheet shows no 🔔 button or push line.
- `components/infrastructure/fan/web/global/concert-sheet`: the 🔔 moment; the guest dialog; the out-of-range notice's 「Sign Up」.
- `components/infrastructure/fan/web/global/bottom-sheet`: the follow action next to the artist name, 「Follow」 / 「Following」, no guest branch.
- `components/infrastructure/fan/web/global/page-help`: no auto-open; tutorial replay buttons; HOMEエリア in the Hype table; seen-flag clearing limited to hype snacks.
- `components/infrastructure/fan/web/global/coach-mark`: the coach mark stays Welcome-only and is told apart from guide moments.
- `components/infrastructure/fan/web/global/celebration-overlay`: no post-signup celebration for a sign-up from 🔔; the new second line.
- `components/infrastructure/fan/web/global/post-signup-dialog`: the 🔔 sign-up path and its notification step title.
- `components/infrastructure/fan/web/global/signup-prompt-banner`: the new banner copy.
- `components/infrastructure/fan/web/global/home-area-selector`: the HOMEエリア title and the new description; the Concerts view opens it only for a signed-in fan without a home area.
- `stories/find-concerts-nearby`: the story is a signed-in fan's.
- `stories/track-ticket-journey`: a guest's 🔔 press opens the sign-up dialog before hosted sign-up.
- `stories/complete-onboarding`: a zero-follow arrival no longer keeps a help auto-open alive.
- `stories/sign-up-or-sign-in`: the sign-up entry points lose the Concerts view's prompt, gain the 🔔 dialog's 「Sign Up」, and read 「Sign Up」 instead of 「登録する」.

No entity, entity operation or usecase changes: every moment's condition reads data the screens already load (follows with their hype levels, journeys, the onboarding state, the push state). No proto change.

## Impact

- Frontend only (fan web): a new guide moment service and surface, Discovery, Concerts view, concert sheet, My Artists, Timetable, Welcome, page help, post-signup dialog, celebration overlay, signup banner, home-area selector, auth callback (the 🔔 sign-up marker), translations (ja, en) and analytics events.
- No backend, proto or infrastructure change.
- Planning artifact outside the spec tree: `specification/docs/fan-story-map.md` records the onboarding story map, as `organizer-console-story-map.md` does for the console.
