# Pass 2 — 人間レビュー資料

Pass 1（12エージェント）→ 語彙拡張で22件確定 → **判定軸の修正**（「観察されるか」ではなく「プロダクト自体の仕様か」）による180行の再審査後。V1/V3/V5/V8 成立。

再審査の結果: OUT→KEEP 反転 16件（API 認可規則→entity/user・entity/organizer、NotFound 契約→entity/user、発見パイプラインの挙動→usecase/concert/search-new-concerts、entity の検証制約 等）、OUT 維持 159件、NEEDS_HUMAN 5件。


## A. openspec から出る spec — 79本（全 requirement が OUT）

誤って捨てられる唯一の関門。**全行を見て、行き先(note)が妥当か確認してください。**

| spec | disposition | req | scen | note |
|---|---|---:|---:|---|
| zitadel-self-hosted-deployment | OUT:design-doc | 20 | 67 | cloud-provisioning/docs/design/zitadel-self-hosted-deployment.md |
| prod-image-pipeline | OUT:runbook | 12 | 49 | cloud-provisioning/docs/runbooks/prod-image-pipeline.md |
| modern-css-platform | OUT:design-doc | 21 | 44 | frontend/docs/design/modern-css-platform.md |
| prod-environment-bootstrap | OUT:design-doc | 15 | 44 | cloud-provisioning/docs/decisions/prod-environment-bootstrap.md (design-doc items); cloud- |
| cube-css-architecture | OUT:lint | 11 | 33 | frontend/stylelint-plugin-cube-css docs (CSS architecture conventions) |
| app-error-log-alerting | OUT:runbook | 14 | 31 | cloud-provisioning/docs/runbooks/app-error-alerting.md |
| entity-test-coverage | OUT:lint | 18 | 31 | backend AGENTS.md / go-tester skill testing standards; frontend entity test conventions |
| usecase-test-coverage | OUT:lint | 8 | 30 | backend test-coverage inventory (discard from openspec) |
| css-linting | OUT:lint | 9 | 27 | frontend/stylelint.config.js (existing tool config, no separate doc needed) |
| frontend-hosting | OUT:runbook | 11 | 27 | cloud-provisioning/docs/runbooks/frontend-hosting.md (design-flavored reqs -> cloud-provis |
| cube-css-layer-constraints | OUT:lint | 5 | 24 | frontend/stylelint-plugin-cube-css docs (layer constraint rules) |
| unified-check-interface | OUT:delete | 2 | 23 | repo-root Makefile / CI workflow YAML (mechanics only, no doc) |
| ci-optimization | OUT:runbook | 11 | 22 | backend/docs/runbooks/ci.md and frontend/docs/runbooks/ci.md |
| css-state-management | OUT:lint | 8 | 21 | frontend coding conventions doc (CSS state-management three-layer contract) |
| cube-css-token-enforcement | OUT:lint | 6 | 20 | frontend/AGENTS.md or a stylelint-plugin-cube-css doc (design-token enforcement rule) |
| gke-standard-infrastructure | OUT:design-doc | 8 | 19 | cloud-provisioning/docs/infrastructure/gke-dev-cluster.md |
| schema-lint | OUT:lint | 10 | 19 | backend/docs/schema-lint.md (or scripts/lint-schema.sh header comment) |
| gemini-searcher-config | OUT:design-doc | 5 | 18 | backend internal config docs (gemini searcher configuration) |
| secret-management | OUT:runbook | 8 | 18 | cloud-provisioning/docs/runbooks/secret-management.md |
| aurelia-template-optimization | OUT:lint | 8 | 17 | frontend coding conventions doc (Aurelia 2 template/binding patterns) |
| frontend-store-cache | OUT:design-doc | 6 | 17 | frontend design doc for the store-cache primitive |
| prod-image-tag-immutability | OUT:runbook | 4 | 17 | cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md |
| argocd-gateway-deployment | OUT:delete | 9 | 16 | cloud-provisioning/k8s (ArgoCD deploy topology and pod-cost overlay mechanics, discard fro |
| argocd-image-automation | OUT:delete | 8 | 16 |  |
| storybook-component-testing | OUT:runbook | 6 | 16 | frontend/docs/testing/storybook.md |
| admin-rpc-server | OUT:design-doc | 6 | 15 | backend/docs/design/admin-rpc-server.md |
| prod-k8s-manifests | OUT:design-doc | 6 | 15 | cloud-provisioning/docs/decisions/prod-k8s-manifests.md |
| zitadel-observability | OUT:runbook | 5 | 15 | cloud-provisioning/docs/runbooks/zitadel-hang.md |
| otel-collector-deployment | OUT:runbook | 7 | 14 | cloud-provisioning/docs/runbooks/otel-collector.md |
| backend-otel-instrumentation | OUT:design-doc | 5 | 13 | backend/docs/design/otel-instrumentation.md |
| cloud-dns-infrastructure | OUT:design-doc | 5 | 13 | cloud-provisioning/docs/design/dns.md |
| cube-css-structural-rules | OUT:lint | 3 | 13 | frontend/.stylelint-plugin (lint rule config, discard from openspec) |
| deployment-infrastructure | OUT:runbook | 10 | 13 | cloud-provisioning/docs/runbooks/pulumi-deployment.md |
| frontend-observability | OUT:design-doc | 3 | 13 | frontend/docs/design/otel-observability.md |
| m3-design-tokens | OUT:lint | 5 | 13 | frontend/docs/design/m3-tokens.md |
| api-rate-limiting | OUT:design-doc | 5 | 12 | backend/docs/design/rate-limiting.md |
| argocd-deployment-alerts | OUT:runbook | 5 | 12 | cloud-provisioning/docs/runbooks/argocd-deployment-alerts.md |
| cube-css-modern-css-rules | OUT:lint | 3 | 12 | frontend stylelint plugin config (already implemented; no separate doc) |
| apex-frontend-serving | OUT:runbook | 4 | 11 | cloud-provisioning/docs/runbooks/apex-frontend-serving.md |
| cube-css-layer-enforcement | OUT:lint | 2 | 11 | frontend stylelint plugin config (already implemented; no separate doc) |
| db-trace-correlation | OUT:design-doc | 4 | 11 | backend/docs/design/db-trace-correlation.md |
| tap-press-feedback | OUT:lint | 5 | 11 | frontend CSS interaction-feedback conventions doc |
| admin-console-hosting | OUT:runbook | 6 | 10 | cloud-provisioning/docs/runbooks/admin-console-hosting.md |
| aurelia-reactivity | OUT:lint | 5 | 10 | frontend/docs/conventions/aurelia-reactivity.md |
| continuous-delivery | OUT:runbook | 9 | 10 | cloud-provisioning/docs/runbooks/continuous-delivery.md |
| feature-flag-management | OUT:design-doc | 5 | 10 | product-analytics/docs/feature-flag-governance.md |
| gcp-cost-guardrails | OUT:runbook | 3 | 10 | cloud-provisioning/docs/runbooks/cost-guardrails.md |
| k8s-resource-right-sizing | OUT:runbook | 2 | 10 | cloud-provisioning/docs/runbooks/k8s-resource-right-sizing.md |
| certificate-manager-integration | OUT:runbook | 6 | 9 | cloud-provisioning/docs/runbooks/certificate-manager.md |
| component-smoke-tests | OUT:delete | 3 | 9 | frontend/test-plans (test/CI inventory, discard from openspec) |
| concert-search-internals | OUT:lint | 5 | 9 | backend/AGENTS.md (Clean Architecture & testing conventions) |
| k8s-service-cross-namespace-routing | OUT:runbook | 6 | 9 | cloud-provisioning/docs/runbooks/k8s-cross-namespace-routing.md |
| workload-naming-convention | OUT:design-doc | 5 | 9 | cloud-provisioning/docs/design/workload-naming-convention.md (migration-procedure req -> c |
| billing-export-infrastructure | OUT:design-doc | 5 | 8 | cloud-provisioning/docs/runbooks/billing-export.md |
| gke-gateway-infrastructure | OUT:design-doc | 6 | 8 | cloud-provisioning/docs/decisions/gke-gateway-infrastructure.md |
| goroutine-leak-detection | OUT:runbook | 3 | 8 | backend/docs/runbooks/goroutine-leak-detection.md |
| zitadel-action-webhook | OUT:design-doc | 3 | 8 | backend design docs (e.g. backend/docs/design/zitadel-webhook.md); network-topology portio |
| atlas-operator | OUT:runbook | 5 | 7 | cloud-provisioning/docs/runbooks/atlas-operator.md |
| e2e-auth-testing | OUT:runbook | 5 | 7 | frontend/docs/runbooks/e2e-auth-testing.md |
| frontend-client-rpc-telemetry | OUT:design-doc | 6 | 7 | frontend internal docs (RPC telemetry design) |
| migration-rebase-guard | OUT:runbook | 3 | 7 | backend/docs/runbooks/migration-drift-guard.md |
| otel-sdk-configuration | OUT:design-doc | 4 | 7 | backend design doc for OTel SDK setup |
| cloud-sql-connector | OUT:runbook | 5 | 6 | backend/docs/runbooks/cloud-sql-connector.md |
| consumer-poison-queue-alerting | OUT:runbook | 2 | 6 | backend ops runbook / cloud-provisioning alert policy (discard from openspec) |
| cube-css-lint-plugin | OUT:lint | 4 | 6 | frontend/stylelint-plugin-cube-css docs (plugin architecture) |
| backend-service-exposure | OUT:runbook | 3 | 5 | cloud-provisioning/docs/runbooks/backend-service-exposure.md |
| bulk-insert-unnest | OUT:design-doc | 2 | 5 | backend internal docs (repository bulk-insert pattern) |
| dev-db-access | OUT:runbook | 4 | 5 | backend/docs/dev-db-access.md |
| localstorage-naming | OUT:lint | 3 | 5 | frontend/AGENTS.md (localStorage key naming convention) |
| private-google-access | OUT:runbook | 3 | 5 | cloud-provisioning/docs/runbooks/private-google-access.md |
| commit-gate-hook | OUT:runbook | 3 | 4 | docs/runbooks/commit-gate-hook.md (one req, code-verifier skill removal, is a one-time obs |
| interceptor-chain-ordering | OUT:design-doc | 2 | 4 | backend/docs/interceptor-ordering.md (or inline code comments per requirement 2) |
| frontend-performance-instrumentation | OUT:runbook | 3 | 3 | frontend observability telemetry (discard from openspec) |
| frontend-router-query-params | OUT:lint | 1 | 3 | frontend internal docs (router coding conventions) |
| pulumi-state-recovery | OUT:runbook | 1 | 3 | cloud-provisioning/docs/runbooks/pulumi-state-recovery.md |
| watermill-structured-logging | OUT:design-doc | 2 | 3 | backend design doc for logging |
| web-push-delivery-alerting | OUT:runbook | 2 | 3 | cloud-provisioning/docs/runbooks/web-push-delivery-alerting.md |
| infra | OUT:design-doc | 2 | 2 | cloud-provisioning/docs/decisions/keda-replica-management.md |
| organizer-console-hosting | OUT:runbook | 2 | 2 | cloud-provisioning/docs/runbooks/organizer-console-hosting.md |

SPLIT spec 内の OUT requirement も含めた OUT 合計: 1675 scenario / 686 req


## B. NEEDS_HUMAN — 残り 30 requirement / 76 scenario


### B-1. アプリ横断の挙動 — 5件。**提案を承認/修正してください**

方針: API の横断規則を entity の不変条件として1箇所に置いたのと同じく、フロントエンドのアプリ全体挙動は app-shell の不変条件として1箇所に置く。

| spec | requirement | scen | 提案 |
|---|---|---:|---|
| frontend-plain-date-lib | Invalid calendar components SHALL NOT silently roll ove | 1 | KEEP → components/entity/event。日付のロールオーバー禁止は Event の日付データの意味論。ライブラリの所在はパスに出さない |
| frontend-testing | Auth retry interceptor refreshes tokens on Unauthentica | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell（上と merge_group=SESSION-REFRESH。http-retry 版が詳細なのでそちらを本文に） |
| http-retry | Deduplicated auth token refresh on concurrent 401s | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell。API 認可規則を entity に1箇所で書くのと同型で、アプリ全体のセッション維持挙動は app-shell の不変条件。frontend-testing の同内容行と merge_group |
| interaction-feedback | Immediate tactile acknowledgement on press | 3 | KEEP → components/infrastructure/ui/fan/global/app-shell。全タップ可能要素に共通のアプリ全体挙動。batch-05 の tap-press-feedback=OUT:lint は再審査対象外だったので、こちらに揃えて KEEP へ戻す候補 |
| non-blocking-menu-navigation | Synchronous prelude remains in loading() | 2 | KEEP → components/infrastructure/ui/fan/global/app-shell。初回描画の状態整合性はルート横断の app-shell 挙動（既に route guard / transition を app-shell に置いた判断と整合） |

### B-2. 個別判断 — 25件

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

## C. 提案された story — 13本

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

重複が疑われる組: `complete-onboarding` / `onboard-new-fan`、`accumulate-guest-data-before-signup` / `preserve-guest-activity-on-sign-up` / `merge-guest-data-on-signup`、`sign-up-or-sign-in` / `maintain-authenticated-session` / `restore-session-on-cold-start`。


## D. merge_group — 15件


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

## 集計

| disposition | req | scen |
|---|---:|---:|
| KEEP | 547 | 1812 |
| OUT:design-doc | 268 | 646 |
| OUT:runbook | 224 | 506 |
| OUT:lint | 170 | 451 |
| NEEDS_HUMAN | 30 | 76 |
| OUT:delete | 24 | 72 |
| DROP:historic | 5 | 14 |
| DROP:duplicate | 3 | 7 |
| DROP:obsolete | 2 | 4 |
