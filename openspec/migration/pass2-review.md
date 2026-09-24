# Pass 2 — 人間レビュー資料

状態: OUT 660 req は導入元 change の archive に再構成済み（80 spec 削除）。origin/main を merge し語彙を同期後コードから再生成、外側の層を `<layer>/<audience>/<web|api>/**` に再配置。NEEDS_HUMAN は 0。

| disposition | req | scen |
|---|---:|---:|
| KEEP | 606 | 1960 |
| OUT:design-doc | 260 | 626 |
| OUT:runbook | 224 | 506 |
| OUT:lint | 158 | 413 |
| OUT:delete | 24 | 72 |
| DROP:obsolete | 6 | 21 |
| DROP:historic | 5 | 14 |
| DROP:duplicate | 3 | 7 |

## 残る判断（3つ）

### 1. archive の訂正を残すか
`2026-05-11-self-hosted-zitadel` の D5（aud claim 検証 → 実装後の signature-only に揃えた）と D2（イメージパスの誤記訂正）。同 change 内の別 delta が実装後の訂正を記していたため design.md を最終設計に揃えた。**推奨: 残す**（design.md はその change の最終設計）。


### 2. story の重複3組を統合するか（提案 13本）

| story | req | scen | 由来 spec |
|---|---:|---:|---|
| stories/accumulate-guest-data-before-signup | 1 | 5 | state-transition-diagram |
| stories/bootstrap-operator-credentials-on-first-sign-in | 1 | 4 | organizer-accounts |
| stories/complete-onboarding | 4 | 20 | frontend-onboarding-flow, frontend-testing, state-transition-diagram |
| stories/maintain-authenticated-session | 2 | 13 | authentication |
| stories/merge-guest-data-on-signup | 5 | 17 | entity-store-layer, guest-data-merge |
| stories/onboard-new-fan | 1 | 5 | concert-search-log |
| stories/preserve-guest-activity-on-sign-up | 1 | 4 | entity-store-layer |
| stories/restore-session-on-cold-start | 1 | 3 | user-auth |
| stories/roam-app-as-guest | 5 | 10 | frontend-route-guard, guest-mode-access |
| stories/set-home-area | 1 | 6 | user-home |
| stories/sign-in-as-organizer | 1 | 4 | organizer-console |
| stories/sign-in-to-admin-console | 3 | 6 | admin-console |
| stories/sign-up-or-sign-in | 1 | 6 | user-auth |

**推奨**: `complete-onboarding` + `onboard-new-fan` → 統合 / `accumulate-guest-data-before-signup` + `preserve-guest-activity-on-sign-up` + `merge-guest-data-on-signup` → 統合 / `sign-up-or-sign-in` / `maintain-authenticated-session` / `restore-session-on-cold-start` → 別ゴールなので統合しない。


### 3. merge_group 21件を承認するか
全件が同じ target に着地。**推奨: 全件承認**。

- **ADMIN-CONSOLE-AUTH** → `stories/sign-in-to-admin-console`: admin-console:Authentication via the admin org with Go / admin-console:Authenticated route guard / admin-console:Post-login welcome placeholder
- **ARTIST-IMAGE-SELECT** → `components/entity/artist`: artist-image:Best Image Selection / artist-image:Fanart Proto Mapper
- **BUBBLE-CAP** → `components/infrastructure/fan/web/route/discovery`: bubble-state-management:BubbleManager provides single source of  / bubble-state-management:BubbleManager enforces capacity through 
- **CONCERT-APPROVE** → `components/usecase/concert/approve`: concert-approval-queue:Approval publishes the concert / concert-approval-queue:Approval reconciles a duplicate existing
- **DISCOVERY-CONSUMER** → `components/usecase/concert/create-from-discovered`: concert-approval-queue:Rejection log is append-only and analysi / concert-approval-queue:Discovery auto-publishes new concerts an
- **ERROR-MAPPING** → `components/adapter/fan/api/rpc/error-mapping`: entity-test-coverage:Error code semantic correctness / usecase-test-coverage:Package utility test coverage
- **GUEST-HYPE-MERGE** → `stories/merge-guest-data-on-signup`: guest-data-merge:Guest hype included in data merge on sig / guest-data-merge:Data Merge on Authentication
- **ISSUANCE** → `components/usecase/ticket/issue-from-captured-win`: ticket-purchase-and-issuance:Idempotent issuance
- **JOURNEY-STATUS** → `components/infrastructure/fan/web/route/dashboard`: journey-status-presentation:Canonical journey-status presentation ma / journey-status-presentation:Status icon and hue assignments / journey-status-presentation:Consistent rendering across components
- **LANG-RESOLUTION** → `components/infrastructure/fan/web/locale/language-resolution`: user-language-preference:Guest Language as Observable Store State / user-language-preference:UserStore Handles NULL Server Preferred 
- **LANG-SWITCH** → `components/infrastructure/fan/web/locale/language-switching`: frontend-i18n:Runtime Language Switching / frontend-i18n:Shared Language Switching Utility
- **LOGO-ANALYSIS** → `components/usecase/artist/sync-artist-image`: logo-color-analysis:Logo Color Extraction / logo-color-analysis:Logo Analysis Integration in Sync Pipeli
- **LOTTERY-DRAW** → `components/usecase/lottery-application/run-draw`: lottery-application:Automatic draw against fixed capacity / lottery-application:Capture winners and release losers at th
- **REDISCOVERY-FILTER** → `components/usecase/concert/search-new-concerts`: concert-approval-queue:Re-discovery dedup consults published an / concert-approval-queue:Re-discovery skips suppressed concerts
- **REFUND** → `components/usecase/order/refund-order`: ticket-purchase-and-issuance:Refund taxonomy — cancellation vs postpo
- **RPC-TIMEOUTS** → `components/adapter/fan/web/rpc/timeouts`: frontend-network-timeouts:Default RPC call timeout / frontend-network-timeouts:RPC timeout value is runtime-configurabl
- **RPC-USER-ID-SCOPING** → `components/entity/user`: rpc-auth-scoping:Explicit user_id in authenticated per-us / rpc-auth-scoping:Creation RPCs are exempt from the user_i
- **SEARCH-LOG** → `components/usecase/concert/search-new-concerts`: concert-search-log:Track Concert Search History / concert-search-log:Track Last Concert Discovery Time
- **SESSION-REFRESH** → `components/infrastructure/fan/web/global/app-shell`: frontend-testing:Auth retry interceptor refreshes tokens  / http-retry:Deduplicated auth token refresh on concu
- **SET-HYPE** → `components/usecase/follow/set-hype`: passion-level:Hype Changes Require Authentication for  / passion-level:Hype Level Persistence / passion-level:SetHype API
- **WEBHOOK-PRE-ACCESS-TOKEN** → `components/adapter/fan/api/webhook/pre-access-token`: zitadel-action-webhook:Pre-Access-Token Webhook Endpoint / zitadel-action-webhook:Webhook Authentication via Zitadel-Issue

**V6**: `Search Concerts by Artist` が `concert-service` と `concert-search` から同じ usecase に着地（merge_group なし）→ 重複なら merge_group、別物なら片方を改名。


## 俺が routine として決めたもの（覆すならここ）

- `event-detail-sheet` を独立 surface に（11 req、コードは `live-highway/event-detail-sheet.ts`）
- フロントエンドの transport 契約（timeout, auth header, AbortSignal）→ `adapter/fan/web/rpc/`
- `intel`（`cmd/intel` 不在）と TicketEmail 由来の1件 → `DROP:obsolete`
- 新規13 req（settlement / dashboard-timetable / beam）を分類。settlement の5件は confidence medium


## 参考: requirement が割り当たらなかった語彙 — 71本

- components/adapter/admin/api/rpc/concert
- components/adapter/admin/api/rpc/order
- components/adapter/admin/api/rpc/organizer
- components/adapter/fan/api/rpc/artist
- components/adapter/fan/api/rpc/concert
- components/adapter/fan/api/rpc/follow
- components/adapter/fan/api/rpc/health
- components/adapter/fan/api/rpc/identity-verification
- components/adapter/fan/api/rpc/lottery
- components/adapter/fan/api/rpc/notification
- components/adapter/fan/api/rpc/organizer
- components/adapter/fan/api/rpc/payout-onboarding
- components/adapter/fan/api/rpc/push-notification
- components/adapter/fan/api/rpc/ticket
- components/adapter/fan/api/rpc/ticket-journey
- components/adapter/fan/api/rpc/user
- components/adapter/organizer/api/rpc/concert
- components/adapter/organizer/api/rpc/lottery
- components/entity/media
- components/entity/staged-concert
- components/entity/verified-identity
- components/infrastructure/admin/web/global/admin-shell
- components/infrastructure/admin/web/route/auth-callback
- components/infrastructure/admin/web/route/organizers
- components/infrastructure/admin/web/route/welcome
- components/infrastructure/fan/web/global/all-nearby
- components/infrastructure/fan/web/global/icons
- components/infrastructure/fan/web/global/inline-error
- components/infrastructure/fan/web/global/notification-mock
- components/infrastructure/fan/web/route/about
- components/infrastructure/fan/web/route/auth-callback
- components/infrastructure/fan/web/route/consent
- components/infrastructure/fan/web/route/lottery-apply
- components/infrastructure/fan/web/route/not-found
- components/infrastructure/fan/web/route/order
- components/infrastructure/fan/web/route/tickets
- components/infrastructure/fan/web/route/verify-callback
- components/infrastructure/organizer/web/route/auth-callback
- components/infrastructure/organizer/web/route/concert-editor
- components/infrastructure/organizer/web/route/concerts
- components/infrastructure/organizer/web/route/denied
- components/infrastructure/organizer/web/route/lottery-phase-editor
- components/infrastructure/organizer/web/route/lottery-status
- components/infrastructure/organizer/web/route/welcome
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
- components/usecase/settlement/ensure-settlement-exists
- components/usecase/ticket/get-my-tickets
- components/usecase/ticket/get-order
- components/usecase/ticket/issue-due-wins
- components/usecase/user/delete
- components/usecase/user/get-by-external-id
- components/usecase/verified-identity/complete-verify
- components/usecase/verified-identity/delete
- components/usecase/verified-identity/get-my-verification-status
- components/usecase/verified-identity/re-check
- components/usecase/verified-identity/start-verify
