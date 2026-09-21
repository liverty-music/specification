# Pass 2 — 人間レビュー資料

Pass 1（12エージェント並列）の結果。V1/V3/V5/V8 は成立。以下の4項目を確認してください。


## A. openspec から出る spec — 89本（全 requirement が OUT）

誤って捨てられる唯一の関門。行き先(note)が妥当か確認。

| spec | disposition | req | scen | note |
|---|---|---:|---:|---|
| zitadel-self-hosted-deployment | OUT:design-doc | 20 | 67 | cloud-provisioning/docs/design/zitadel-self-hosted-deployment.md |
| prod-image-pipeline | OUT:runbook | 12 | 49 | cloud-provisioning/docs/runbooks/prod-image-pipeline.md |
| gemini-grounded-extract-and-coerce | OUT:design-doc | 19 | 46 | backend/internal/infrastructure/gcp/gemini/design.md |
| modern-css-platform | OUT:design-doc | 21 | 44 | frontend/docs/design/modern-css-platform.md |
| prod-environment-bootstrap | OUT:design-doc | 15 | 44 | cloud-provisioning/docs/decisions/prod-environment-bootstrap.md (design-doc item |
| product-analytics | OUT:design-doc | 14 | 40 | docs/analytics/event-catalog.md (process items) plus a design-doc for SDK/pipeli |
| cube-css-architecture | OUT:lint | 11 | 33 | frontend/stylelint-plugin-cube-css docs (CSS architecture conventions) |
| app-error-log-alerting | OUT:runbook | 14 | 31 | cloud-provisioning/docs/runbooks/app-error-alerting.md |
| entity-test-coverage | OUT:lint | 18 | 31 | backend AGENTS.md / go-tester skill testing standards; frontend entity test conv |
| usecase-test-coverage | OUT:lint | 8 | 30 | backend test-coverage inventory (discard from openspec) |
| css-linting | OUT:lint | 9 | 27 | frontend/stylelint.config.js (existing tool config, no separate doc needed) |
| frontend-hosting | OUT:runbook | 11 | 27 | cloud-provisioning/docs/runbooks/frontend-hosting.md (design-flavored reqs -> cl |
| cube-css-layer-constraints | OUT:lint | 5 | 24 | frontend/stylelint-plugin-cube-css docs (layer constraint rules) |
| unified-check-interface | OUT:delete | 2 | 23 | repo-root Makefile / CI workflow YAML (mechanics only, no doc) |
| ci-optimization | OUT:runbook | 11 | 22 | backend/docs/runbooks/ci.md and frontend/docs/runbooks/ci.md |
| layout-assertions | OUT:runbook | 6 | 22 | frontend/e2e (test conventions, no dedicated doc) |
| css-state-management | OUT:lint | 8 | 21 | frontend coding conventions doc (CSS state-management three-layer contract) |
| cube-css-token-enforcement | OUT:lint | 6 | 20 | frontend/AGENTS.md or a stylelint-plugin-cube-css doc (design-token enforcement  |
| gke-standard-infrastructure | OUT:design-doc | 8 | 19 | cloud-provisioning/docs/infrastructure/gke-dev-cluster.md |
| schema-lint | OUT:lint | 10 | 19 | backend/docs/schema-lint.md (or scripts/lint-schema.sh header comment) |
| gemini-searcher-config | OUT:design-doc | 5 | 18 | backend internal config docs (gemini searcher configuration) |
| secret-management | OUT:runbook | 8 | 18 | cloud-provisioning/docs/runbooks/secret-management.md |
| aurelia-template-optimization | OUT:lint | 8 | 17 | frontend coding conventions doc (Aurelia 2 template/binding patterns) |
| frontend-store-cache | OUT:design-doc | 6 | 17 | frontend design doc for the store-cache primitive |
| jetstream-consumer-reliability | OUT:design-doc | 9 | 17 | backend/docs/design/jetstream-consumer-reliability.md (operational-flavored reqs |
| prod-image-tag-immutability | OUT:runbook | 4 | 17 | cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md |
| argocd-gateway-deployment | OUT:delete | 9 | 16 | cloud-provisioning/k8s (ArgoCD deploy topology and pod-cost overlay mechanics, d |
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
| frontend-plain-date-lib | OUT:design-doc | 6 | 13 | frontend/src/lib/plain-date design rationale (no existing doc file identified);  |
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
| workload-naming-convention | OUT:design-doc | 5 | 9 | cloud-provisioning/docs/design/workload-naming-convention.md (migration-procedur |
| billing-export-infrastructure | OUT:design-doc | 5 | 8 | cloud-provisioning/docs/runbooks/billing-export.md |
| connect-rpc-cors | OUT:design-doc | 5 | 8 | backend/internal/... CORS middleware config (discard from openspec) |
| database-migration | OUT:design-doc | 5 | 8 | backend internal docs (migration runtime behavior) |
| gke-gateway-infrastructure | OUT:design-doc | 6 | 8 | cloud-provisioning/docs/decisions/gke-gateway-infrastructure.md |
| goroutine-leak-detection | OUT:runbook | 3 | 8 | backend/docs/runbooks/goroutine-leak-detection.md |
| zitadel-action-webhook | OUT:design-doc | 3 | 8 | backend design docs (e.g. backend/docs/design/zitadel-webhook.md); network-topol |
| atlas-operator | OUT:runbook | 5 | 7 | cloud-provisioning/docs/runbooks/atlas-operator.md |
| database | OUT:runbook | 4 | 7 | cloud-provisioning/docs/runbooks/database.md (design-flavored reqs -> cloud-prov |
| e2e-auth-testing | OUT:runbook | 5 | 7 | frontend/docs/runbooks/e2e-auth-testing.md |
| email-provider | OUT:design-doc | 5 | 7 | cloud-provisioning/src/zitadel (SMTP infra provisioning, discard from openspec) |
| frontend-client-rpc-telemetry | OUT:design-doc | 6 | 7 | frontend internal docs (RPC telemetry design) |
| migration-rebase-guard | OUT:runbook | 3 | 7 | backend/docs/runbooks/migration-drift-guard.md |
| otel-sdk-configuration | OUT:design-doc | 4 | 7 | backend design doc for OTel SDK setup |
| semantic-dom | OUT:lint | 4 | 7 | frontend/docs/conventions/semantic-dom.md |
| cloud-sql-connector | OUT:runbook | 5 | 6 | backend/docs/runbooks/cloud-sql-connector.md |
| consumer-poison-queue-alerting | OUT:runbook | 2 | 6 | backend ops runbook / cloud-provisioning alert policy (discard from openspec) |
| cube-css-lint-plugin | OUT:lint | 4 | 6 | frontend/stylelint-plugin-cube-css docs (plugin architecture) |
| backend-service-exposure | OUT:runbook | 3 | 5 | cloud-provisioning/docs/runbooks/backend-service-exposure.md |
| bulk-insert-unnest | OUT:design-doc | 2 | 5 | backend internal docs (repository bulk-insert pattern) |
| dev-db-access | OUT:runbook | 4 | 5 | backend/docs/dev-db-access.md |
| localstorage-naming | OUT:lint | 3 | 5 | frontend/AGENTS.md (localStorage key naming convention) |
| private-google-access | OUT:runbook | 3 | 5 | cloud-provisioning/docs/runbooks/private-google-access.md |
| commit-gate-hook | OUT:runbook | 3 | 4 | docs/runbooks/commit-gate-hook.md (one req, code-verifier skill removal, is a on |
| interceptor-chain-ordering | OUT:design-doc | 2 | 4 | backend/docs/interceptor-ordering.md (or inline code comments per requirement 2) |
| frontend-performance-instrumentation | OUT:runbook | 3 | 3 | frontend observability telemetry (discard from openspec) |
| frontend-router-query-params | OUT:lint | 1 | 3 | frontend internal docs (router coding conventions) |
| pulumi-state-recovery | OUT:runbook | 1 | 3 | cloud-provisioning/docs/runbooks/pulumi-state-recovery.md |
| watermill-structured-logging | OUT:design-doc | 2 | 3 | backend design doc for logging |
| web-push-delivery-alerting | OUT:runbook | 2 | 3 | cloud-provisioning/docs/runbooks/web-push-delivery-alerting.md |
| infra | OUT:design-doc | 2 | 2 | cloud-provisioning/docs/decisions/keda-replica-management.md |
| organizer-console-hosting | OUT:runbook | 2 | 2 | cloud-provisioning/docs/runbooks/organizer-console-hosting.md |

合計 1300 scenario。SPLIT spec 内の OUT requirement を含めると OUT は 1704 scenario。


## B. NEEDS_HUMAN — 55 requirement / 161 scenario（26 spec）


### 1. admin / organizer アプリの画面が語彙に無い — 3件 / 11 scenario

| spec | requirement | scen | rationale |
|---|---|---:|---|
| admin-concert-management | Admin console presents approved concerts grouped by artist a | 3 | admin console UI grouping/delete-confirmation screen has no route/global surface yet in vocabulary (admin fron |
| concert-approval-queue | Admin console approval-queue UI | 5 | The bundle-isolated admin/ app has no matching entry in vocabulary's ui/route or ui/global lists (those cover  |
| organizer-console | Route guard admits only owner-role operators | 3 | guard applies across all organizer-console routes, not one route or an existing global surface in vocabulary |

### 2. Zitadel ホストのログイン画面が語彙に無い — 4件 / 16 scenario

| spec | requirement | scen | rationale |
|---|---|---:|---|
| identity-management | Configure Login Policy | 2 | Fan observes passwordless enforcement on the hosted Login UI, but no vocabulary route/component covers the Zit |
| identity-management | Configure Login UI Branding | 5 | Fan observes brand colors on the hosted Login UI v2, but no vocabulary route/component or infra kind covers Zi |
| identity-management | Configure OIDC Token Lifetimes | 3 | Fan-observable session/expiry behavior (30m access, 90d refresh), but no vocabulary route/component covers Zit |
| organizer-tenancy | Organizer tenant orgs use a passkey-primary login policy wit | 6 | Organizer actor directly experiences passkey login + recovery, but no vocabulary route/component covers the Zi |

### 3. トップレベル surface（app-shell / event-card / event-detail-sheet 等）が語彙に無い — 10件 / 33 scenario

| spec | requirement | scen | rationale |
|---|---|---:|---|
| app-shell-layout | Brand Identity Elements | 4 | No vocabulary target for app-level branding/favicon/manifest chrome; does not fit an existing route, global su |
| app-shell-layout | Page Transition Animations | 3 | Shell-wide route-transition animation applies to every route; no matching route or global-surface vocabulary t |
| artist-image-ui | Event Card Logo Display | 4 | EventCard is rendered across dashboard/welcome/discovery but vocabulary has no ui/global event-card surface en |
| artist-image-ui | Fanart Data Propagation | 3 | Frontend service-layer mapping that feeds the (currently unmapped) event-card/detail-sheet surfaces above |
| design-system | Page Shell Component | 4 | proposed <page-shell> global surface is not present in vocabulary.tsv (closest is page-header) |
| event-card-glow | Matched event card glow opacity | 1 | event-card has no dedicated ui/global vocabulary entry (cf. batch-01 artist-image-ui precedent); the glow is a |
| frontend-testing | Event card computes display properties | 2 | EventCard display logic; no vocabulary event-card surface (see artist-image-ui) |
| logo-color-analysis | Frontend Background Color Derivation | 4 | user-facing (event card --artist-hue) but no matching ui/global surface (e.g. event-card/artist-image) in voca |
| shell-layout | Overlay elements excluded from grid flow | 5 | app-shell-level CSS Grid architecture spanning multiple overlay CEs; no 'app-shell' surface in vocabulary |
| shell-layout | Document root is a non-scrolling frame | 3 | app-shell-level html/body scroll-containment architecture, no fitting vocabulary surface |

### 4. 横断的挙動（認可規約 / ルーター / ゲスト方針） — 14件 / 41 scenario

| spec | requirement | scen | rationale |
|---|---|---:|---|
| frontend-testing | Auth hook guards all authenticated routes | 4 | AuthHook route guard is cross-cutting; no matching infra kind in vocabulary |
| frontend-testing | Auth retry interceptor refreshes tokens on Unauthenticated e | 3 | Auth-retry interceptor is transport-level; not a UI surface or listed infra kind |
| frontend-testing | Retry interceptor applies exponential backoff on transient e | 4 | Generic retry interceptor is transport-level; not a UI surface or listed infra kind |
| guest-mode-access | Guest Free Navigation After Dashboard | 2 | cross-route navigation policy; no single route/global-surface vocabulary entry fits and it is not a concrete s |
| guest-mode-access | Account-Only Features Hidden, Not Blocked | 2 | cross-route UI policy applied per-screen; no single route/global-surface vocabulary entry fits |
| http-retry | Deduplicated auth token refresh on concurrent 401s | 3 | user-visible via session-clear/redirect to /welcome on failure, but no vocabulary target for a cross-cutting R |
| id-resolution | Handlers return NotFound when user record does not exist | 1 | cross-cutting NotFound behavior spans Follow/TicketJourney/TicketEmail usecases, no single vocabulary usecase/ |
| interaction-feedback | Immediate tactile acknowledgement on press | 3 | App-wide cross-cutting press-feedback primitive applied to every tappable control; no matching route/global vo |
| non-blocking-menu-navigation | Menu-tab navigation attaches the view before data resolves | 2 | cross-route router behavior (My Artists/Dashboard/Discovery loading() hook) with no fitting single vocabulary  |
| non-blocking-menu-navigation | In-flight state is shown via the route's existing UI | 2 | same cross-route (My Artists/Dashboard/Discovery) scope issue as sibling requirement |
| non-blocking-menu-navigation | Late-arriving data renders regardless of attach order | 2 | cross-route rendering guarantee (incl. Discovery bubbles canvas), no single fitting vocabulary target |
| organizer-rpc-server | Org-scoped authorization from the role claim | 8 | cross-cutting auth spanning both Get and ListArtists, no single fitting usecase target |
| rpc-auth-scoping | Explicit user_id in authenticated per-user RPC bodies | 4 | cross-cutting convention over every per-user RPC handler, no single usecase/route target |
| rpc-auth-scoping | Creation RPCs are exempt from the user_id convention | 1 | corollary of the sibling requirement, same cross-cutting scope issue |

### 5. その他（個別判断） — 24件 / 60 scenario

| spec | requirement | scen | rationale |
|---|---|---:|---|
| artist-image-ui | Event Detail Sheet Hero Image | 3 | EventDetailSheet has no vocabulary entry (only the generic bottom-sheet exists, which this specializes) |
| entity-domain-logic | Parsed email data journey status mapping | 6 | Scenarios reference Purchased/Entered/Refunded phases and automatic status derivation from email, but ticket_j |
| entity-store-layer | Boot Reconciliation of Unmerged Guest Data | 3 | Unclear whether this retry/receipt bookkeeping is an independently testable user guarantee beyond the continui |
| frontend-network-timeouts | Default RPC call timeout | 3 | Cross-app RPC transport deadline, not scoped to one route; vocabulary has no networking/transport infra kind |
| frontend-network-timeouts | RPC timeout value is runtime-configurable | 3 | Same shared-transport config surface as the default-timeout requirement above; no matching vocabulary target |
| frontend-runtime-config | Bootstrap failures SHALL surface a static error page | 2 | genuinely user-visible failure page, but it is explicitly non-Aurelia (bypasses all ui/global components) so n |
| frontend-testing | Auth status delegates to auth service | 3 | AuthStatus component has no matching ui/global vocabulary entry |
| frontend-testing | gRPC transport injects auth headers | 2 | gRPC auth-header injection is transport-level plumbing; tie-break excludes components/adapter |
| frontend-testing | Concert service forwards RPC calls with AbortSignal | 3 | ConcertService RPC forwarding/AbortSignal is transport-level plumbing with no clear target |
| frontend-testing | Event detail sheet computes URLs and handles touch dismiss | 4 | EventDetailSheet has no vocabulary entry distinct from the generic bottom-sheet primitive |
| intel | Live Information Crawling | 1 | crawling capability likely feeds ConcertUseCase.SearchNewConcerts but the intel CLI's exact relationship to th |
| interaction-feedback | Haptic feedback for meaningful confirmations | 2 | App-wide generalized haptic-feedback primitive (follow/unfollow and beyond); no matching route/global vocabula |
| ticket-journey | Ticket Status UI visibility | 2 | EventDetailSheet Ticket Status section is a cross-route UI surface with no matching components/infrastructure/ |
| ticket-journey | Ticket Status UI two-phase layout | 2 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status cumulative progress display | 3 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status selection contrast | 1 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status semantic color and non-color cues | 2 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status outcome gating | 3 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Status radiogroup accessibility | 1 | same EventDetailSheet Ticket Status surface, no matching vocabulary target |
| ticket-journey | Ticket Journey UI is independent of ticket sales | 2 | governs visibility of the same unregistered EventDetailSheet Ticket Status surface plus concert-card badge, no |
| ticket-purchase-and-issuance | Issue from ④'s captured winning payment | 3 | Order-creation usecase triggered by lottery capture signal; vocabulary has no order/ticket-issuance usecase en |
| ticket-purchase-and-issuance | Idempotent issuance | 1 | Issuance-replay-safety usecase behavior; no order/ticket-issuance usecase in vocabulary |
| ticket-purchase-and-issuance | Capture succeeded but issuance failed | 1 | Post-capture reconciliation/refund usecase behavior; no matching usecase target |
| ticket-purchase-and-issuance | Refund taxonomy — cancellation vs postponement | 4 | Refund-policy usecase spans Event/Ticket/Order with execution owned by an out-of-batch capability; no matching |

## C. 提案された story — 13本（語彙に無い新規提案。命名と統合を判断）

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
| stories/roam-app-as-guest | 3 | 6 | frontend-route-guard |
| stories/set-home-area | 1 | 6 | user-home |
| stories/sign-in-as-organizer | 1 | 4 | organizer-console |
| stories/sign-in-to-admin-console | 3 | 6 | admin-console |
| stories/sign-up-or-sign-in | 1 | 6 | user-auth |

## D. merge_group — 13件（複数の旧 requirement を1本に統合してよいか）


**ADMIN-CONSOLE-AUTH** → `stories/sign-in-to-admin-console`
- admin-console / Authentication via the admin org with Google Workspace IDP (3 scen)
- admin-console / Authenticated route guard (2 scen)
- admin-console / Post-login welcome placeholder (1 scen)

**BUBBLE-CAP** → `components/infrastructure/ui/route/discovery`
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

**JOURNEY-STATUS** → `components/infrastructure/ui/route/dashboard`
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

**SEARCH-LOG** → `components/usecase/concert/search-new-concerts`
- concert-search-log / Track Concert Search History (3 scen)
- concert-search-log / Track Last Concert Discovery Time (3 scen)

**SET-HYPE** → `components/usecase/follow/set-hype`
- passion-level / Hype Changes Require Authentication for Server-Side Persistence (2 scen)
- passion-level / Hype Level Persistence (1 scen)
- passion-level / SetHype API (3 scen)

**V6 警告**: `Search Concerts by Artist` が `concert-service` と `concert-search` から同じ `components/usecase/concert/search-new-concerts` に着地（merge_group なし）。重複なら merge_group、別物なら片方を改名。


## E. requirement が1本も割り当たらなかった語彙 — 40本（参考。spec が無い＝未記述の振る舞い）

- components/entity/media
- components/entity/organizer
- components/entity/settlement
- components/entity/staged-concert
- components/entity/verified-identity
- components/usecase/artist/resolve-canonical-name
- components/usecase/artist/list
- components/usecase/artist/get-official-site
- components/usecase/concert/update-draft
- components/usecase/concert/cancel
- components/usecase/concert/regenerate-token
- components/usecase/concert/list-by-follower
- components/usecase/verified-identity/start-verify
- components/usecase/verified-identity/complete-verify
- components/usecase/verified-identity/re-check
- components/usecase/verified-identity/get-my-verification-status
- components/usecase/verified-identity/delete
- components/usecase/lottery-application/set-phase-verification-requirement
- components/usecase/lottery-application/create-authorization
- components/usecase/lottery-application/withdraw-application
- components/usecase/lottery-application/get-my-application
- components/usecase/lottery-application/get-lottery-phase-status
- components/usecase/lottery-application/draw-due-phases
- components/usecase/notification/mark-dismissed
- components/usecase/organizer/get-by-zitadel-org-id
- components/usecase/organizer/disassociate-artist
- components/usecase/user/get-by-external-id
- components/usecase/user/delete
- components/infrastructure/ui/route/about
- components/infrastructure/ui/route/auth-callback
- components/infrastructure/ui/route/consent
- components/infrastructure/ui/route/lottery-apply
- components/infrastructure/ui/route/not-found
- components/infrastructure/ui/route/order
- components/infrastructure/ui/route/tickets
- components/infrastructure/ui/route/verify-callback
- components/infrastructure/ui/global/all-nearby
- components/infrastructure/ui/global/icons
- components/infrastructure/ui/global/inline-error
- components/infrastructure/ui/global/notification-mock

## 集計

| disposition | req | scen |
|---|---:|---:|
| KEEP | 509 | 1698 |
| OUT:design-doc | 280 | 672 |
| OUT:runbook | 225 | 509 |
| OUT:lint | 170 | 451 |
| NEEDS_HUMAN | 55 | 161 |
| OUT:delete | 24 | 72 |
| DROP:historic | 5 | 14 |
| DROP:duplicate | 3 | 7 |
| DROP:obsolete | 2 | 4 |
