# Pass 2 — 人間レビュー資料

状態: OUT 660 requirement は導入元 change の archive（design.md）に再構成済みで main spec から除去、80 spec 削除（コミット `22894ad`）。**A 節（OUT spec の行き先確認）は完了扱い**。残るのは KEEP 側の配置判断。

| disposition | req | scen |
|---|---:|---:|
| KEEP | 564 | 1858 |
| OUT:design-doc | 260 | 626 |
| OUT:runbook | 224 | 506 |
| OUT:lint | 158 | 413 |
| NEEDS_HUMAN | 31 | 78 |
| OUT:delete | 24 | 72 |
| DROP:historic | 5 | 14 |
| DROP:obsolete | 4 | 14 |
| DROP:duplicate | 3 | 7 |

残存 main spec 129本 / 607 req / 1,971 scen（KEEP 564 + DROP 12 + NEEDS_HUMAN 31。Phase 3 の入力）


## 再構成で生じた判断点（archive の内容に関わる。確認推奨）

- **日本語 design.md への英語追記（2ファイル）**: `2026-02-24-remove-audit-timestamps`, `2026-03-17-make-dom-semantic`。エージェントはグローバル規約（文書は英語）を優先した。ファイルの言語に合わせて和訳するか、そのままか

- **過去の誤った決定の訂正**: `2026-05-11-self-hosted-zitadel` の D5（aud claim 検証 → signature-only に訂正）と D2（イメージパスの誤記訂正）。同 change 内の別 delta が実装後の訂正を記していたため、design.md を最終設計に揃えた。「その時点の決定」を残す方針なら差し戻し

- **untraced 38 requirement**: 導入 change を delta から特定できず、git 履歴のみに残る（`authentication` の JWKS caching 等、最初期の spec）


## B-1. アプリ横断のフロントエンド挙動 — 5件（提案の承認）

| spec | requirement | scen | 提案 |
|---|---|---:|---|
| frontend-plain-date-lib | Invalid calendar components SHALL NOT silently roll ove | 1 | KEEP → components/entity/event |
| frontend-testing | Auth retry interceptor refreshes tokens on Unauthentica | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell（同上） |
| http-retry | Deduplicated auth token refresh on concurrent 401s | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell（merge_group=SESSION-REFRESH） |
| interaction-feedback | Immediate tactile acknowledgement on press | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell |
| non-blocking-menu-navigation | Synchronous prelude remains in loading() | 2 | KEEP → components/infrastructure/ui/fan/global/app-shell |

## B-2. 個別判断 — 26件

| spec | requirement | scen | rationale |
|---|---|---:|---|
| artist-image-ui | Event Detail Sheet Hero Image | 3 | EventDetailSheet has no vocabulary entry (only the generic bottom-sheet exists, which this specializes) |
| design-system | Page Shell Component | 4 | proposed <page-shell> global surface is not present in vocabulary.tsv (closest is page-header) |
| entity-domain-logic | Parsed email data journey status mapping | 6 | Scenarios reference Purchased/Entered/Refunded phases and automatic status derivation from email, but ticket_journey.pro |
| entity-store-layer | Boot Reconciliation of Unmerged Guest Data | 3 | Unclear whether this retry/receipt bookkeeping is an independently testable user guarantee beyond the continuity already |
| frontend-network-timeouts | Default RPC call timeout | 3 | Cross-app RPC transport deadline, not scoped to one route; vocabulary has no networking/transport infra kind |
| frontend-network-timeouts | RPC timeout value is runtime-configurable | 3 | Same shared-transport config surface as the default-timeout requirement above; no matching vocabulary target |
| frontend-runtime-config | Bootstrap failures SHALL surface a static error page | 2 | genuinely user-visible failure page, but it is explicitly non-Aurelia (bypasses all ui/global components) so no vocabula |
| frontend-testing | Auth status delegates to auth service | 3 | AuthStatus component has no matching ui/global vocabulary entry |
| frontend-testing | gRPC transport injects auth headers | 2 | gRPC auth-header injection is transport-level plumbing; tie-break excludes components/adapter |
| frontend-testing | Concert service forwards RPC calls with AbortSignal | 3 | ConcertService RPC forwarding/AbortSignal is transport-level plumbing with no clear target |
| frontend-testing | Event detail sheet computes URLs and handles touch dism | 4 | EventDetailSheet has no vocabulary entry distinct from the generic bottom-sheet primitive |
| intel | Live Information Crawling | 1 | crawling capability likely feeds ConcertUseCase.SearchNewConcerts but the intel CLI's exact relationship to that RPC/use |
| interaction-feedback | Haptic feedback for meaningful confirmations | 2 | App-wide generalized haptic-feedback primitive (follow/unfollow and beyond); no matching route/global vocabulary target. |
| ticket-journey | Ticket Status UI visibility | 2 | EventDetailSheet Ticket Status section is a cross-route UI surface with no matching components/infrastructure/ui/global/ |
| ticket-journey | Ticket Status UI two-phase layout | 2 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status cumulative progress display | 3 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status selection contrast | 1 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status semantic color and non-color cues | 2 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status outcome gating | 3 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status radiogroup accessibility | 1 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Journey UI is independent of ticket sales | 2 | governs visibility of the same unregistered EventDetailSheet Ticket Status surface plus concert-card badge, no matching  |
| ticket-purchase-and-issuance | Issue from ④'s captured winning payment | 3 | Order-creation usecase triggered by lottery capture signal; vocabulary has no order/ticket-issuance usecase entries yet |
| ticket-purchase-and-issuance | Idempotent issuance | 1 | Issuance-replay-safety usecase behavior; no order/ticket-issuance usecase in vocabulary |
| ticket-purchase-and-issuance | Capture succeeded but issuance failed | 1 | Post-capture reconciliation/refund usecase behavior; no matching usecase target |
| ticket-purchase-and-issuance | Refund taxonomy — cancellation vs postponement | 4 | Refund-policy usecase spans Event/Ticket/Order with execution owned by an out-of-batch capability; no matching usecase t |
| usecase-test-coverage | User event consumer test coverage | 2 | [re-audit-2] Describes real background-job behavior (USER.created CloudEvent drives a usecase call; malformed payload is |

## C. 提案された story — 13本（命名・統合）

| story | req | scen | 由来 spec |
|---|---:|---:|---|
| stories/accumulate-guest-data-before-signup | 1 | 5 | state-transition-diagram |
| stories/bootstrap-operator-credentials-on-first-sign-in | 1 | 4 | organizer-accounts |
| stories/complete-onboarding | 4 | 20 | frontend-onboarding-flow, frontend-testing, state-transition-diagram |
| stories/maintain-authenticated-session | 2 | 13 | authentication |
| stories/merge-guest-data-on-signup | 4 | 14 | guest-data-merge |
| stories/onboard-new-fan | 1 | 5 | concert-search-log |
| stories/preserve-guest-activity-on-sign-up | 1 | 4 | entity-store-layer |
| stories/restore-session-on-cold-start | 1 | 3 | user-auth |
| stories/roam-app-as-guest | 5 | 10 | frontend-route-guard, guest-mode-access |
| stories/set-home-area | 1 | 6 | user-home |
| stories/sign-in-as-organizer | 1 | 4 | organizer-console |
| stories/sign-in-to-admin-console | 3 | 6 | admin-console |
| stories/sign-up-or-sign-in | 1 | 6 | user-auth |

重複疑い: `complete-onboarding` / `onboard-new-fan`、`accumulate-guest-data-before-signup` / `preserve-guest-activity-on-sign-up` / `merge-guest-data-on-signup`、`sign-up-or-sign-in` / `maintain-authenticated-session` / `restore-session-on-cold-start`。


## D. merge_group — 17件（統合の可否）


**ADMIN-CONSOLE-AUTH** → `stories/sign-in-to-admin-console`
- admin-console / Authentication via the admin org with Google Workspace IDP (3 scen)
- admin-console / Authenticated route guard (2 scen)
- admin-console / Post-login welcome placeholder (1 scen)

**ARTIST-IMAGE-SELECT** → `components/entity/artist`
- artist-image / Best Image Selection (2 scen)
- artist-image / Fanart Proto Mapper (2 scen)

**BUBBLE-CAP** → `components/infrastructure/ui/fan/route/discovery`
- bubble-state-management / BubbleManager provides single source of truth for bubble lifecycle (4 scen)
- bubble-state-management / BubbleManager enforces capacity through coordinated eviction (2 scen)

**CONCERT-APPROVE** → `components/usecase/concert/approve`
- concert-approval-queue / Approval publishes the concert (3 scen)
- concert-approval-queue / Approval reconciles a duplicate existing event (4 scen)

**DISCOVERY-CONSUMER** → `components/usecase/concert/create-from-discovered`
- concert-approval-queue / Rejection log is append-only and analysis-only (1 scen)
- concert-approval-queue / Discovery auto-publishes new concerts and stages only conflicts (5 scen)

**ERROR-MAPPING** → `components/adapter/rpc/error-mapping`
- entity-test-coverage / Error code semantic correctness (3 scen)
- usecase-test-coverage / Package utility test coverage (2 scen)

**GUEST-HYPE-MERGE** → `stories/merge-guest-data-on-signup`
- guest-data-merge / Guest hype included in data merge on signup (3 scen)
- guest-data-merge / Data Merge on Authentication (4 scen)

**JOURNEY-STATUS** → `components/infrastructure/ui/fan/route/dashboard`
- journey-status-presentation / Canonical journey-status presentation map (2 scen)
- journey-status-presentation / Status icon and hue assignments (4 scen)
- journey-status-presentation / Consistent rendering across components (1 scen)

**LANG-RESOLUTION** → `components/infrastructure/locale/language-resolution`
- user-language-preference / Guest Language as Observable Store State (2 scen)
- user-language-preference / UserStore Handles NULL Server Preferred Language (1 scen)

**LANG-SWITCH** → `components/infrastructure/locale/language-switching`
- frontend-i18n / Runtime Language Switching (3 scen)
- frontend-i18n / Shared Language Switching Utility (3 scen)

**LOGO-ANALYSIS** → `components/usecase/artist/sync-artist-image`
- logo-color-analysis / Logo Color Extraction (4 scen)
- logo-color-analysis / Logo Analysis Integration in Sync Pipeline (4 scen)

**LOTTERY-DRAW** → `components/usecase/lottery-application/run-draw`
- lottery-application / Automatic draw against fixed capacity (5 scen)
- lottery-application / Capture winners and release losers at the draw (3 scen)

**REDISCOVERY-FILTER** → `components/usecase/concert/search-new-concerts`
- concert-approval-queue / Re-discovery dedup consults published and pending state (3 scen)
- concert-approval-queue / Re-discovery skips suppressed concerts (2 scen)

**RPC-USER-ID-SCOPING** → `components/entity/user`
- rpc-auth-scoping / Explicit user_id in authenticated per-user RPC bodies (4 scen)
- rpc-auth-scoping / Creation RPCs are exempt from the user_id convention (1 scen)

**SEARCH-LOG** → `components/usecase/concert/search-new-concerts`
- concert-search-log / Track Concert Search History (3 scen)
- concert-search-log / Track Last Concert Discovery Time (3 scen)

**SET-HYPE** → `components/usecase/follow/set-hype`
- passion-level / Hype Changes Require Authentication for Server-Side Persistence (2 scen)
- passion-level / Hype Level Persistence (1 scen)
- passion-level / SetHype API (3 scen)

**WEBHOOK-PRE-ACCESS-TOKEN** → `components/adapter/webhook/pre-access-token`
- zitadel-action-webhook / Pre-Access-Token Webhook Endpoint (2 scen)
- zitadel-action-webhook / Webhook Authentication via Zitadel-Issued JWT Signature (3 scen)

**V6**: `Search Concerts by Artist` が `concert-service` と `concert-search` から同じ usecase に着地（merge_group なし）。


## E. requirement が割り当たらなかった語彙 — 50本（参考）

- components/entity/media
- components/entity/settlement
- components/entity/staged-concert
- components/entity/verified-identity
- components/infrastructure/ui/admin/global/admin-shell
- components/infrastructure/ui/admin/route/auth-callback
- components/infrastructure/ui/admin/route/organizers
- components/infrastructure/ui/admin/route/welcome
- components/infrastructure/ui/fan/global/all-nearby
- components/infrastructure/ui/fan/global/icons
- components/infrastructure/ui/fan/global/inline-error
- components/infrastructure/ui/fan/global/notification-mock
- components/infrastructure/ui/fan/route/about
- components/infrastructure/ui/fan/route/auth-callback
- components/infrastructure/ui/fan/route/consent
- components/infrastructure/ui/fan/route/lottery-apply
- components/infrastructure/ui/fan/route/not-found
- components/infrastructure/ui/fan/route/order
- components/infrastructure/ui/fan/route/tickets
- components/infrastructure/ui/fan/route/verify-callback
- components/infrastructure/ui/organizer/route/auth-callback
- components/infrastructure/ui/organizer/route/concert-editor
- components/infrastructure/ui/organizer/route/concerts
- components/infrastructure/ui/organizer/route/denied
- components/infrastructure/ui/organizer/route/lottery-phase-editor
- components/infrastructure/ui/organizer/route/lottery-status
- components/infrastructure/ui/organizer/route/welcome
- components/usecase/artist/get-official-site
- components/usecase/artist/list
- components/usecase/artist/resolve-canonical-name
- components/usecase/concert/cancel
- components/usecase/concert/list-by-follower
- components/usecase/concert/regenerate-token
- components/usecase/concert/update-draft
- components/usecase/lottery-application/create-authorization
- components/usecase/lottery-application/draw-due-phases
- components/usecase/lottery-application/get-lottery-phase-status
- components/usecase/lottery-application/get-my-application
- components/usecase/lottery-application/set-phase-verification-requirement
- components/usecase/lottery-application/withdraw-application
- components/usecase/notification/mark-dismissed
- components/usecase/organizer/disassociate-artist
- components/usecase/organizer/get-by-zitadel-org-id
- components/usecase/user/delete
- components/usecase/user/get-by-external-id
- components/usecase/verified-identity/complete-verify
- components/usecase/verified-identity/delete
- components/usecase/verified-identity/get-my-verification-status
- components/usecase/verified-identity/re-check
- components/usecase/verified-identity/start-verify
