## Context

prod 環境を 5/13 に立ち上げ、5/18 に dev cluster を削除して安定運用に入ったのち、課金実績 (May 19-28 の SKU 別 CSV) を分析した結果、月額 ¥30,000 ($200) ペースで以下の 6 SKU が突出していた:

| SKU | 月額換算 | 削減可否 |
|---|---|---|
| Gemini API (input + output + grounding) | ~¥13,000 | 別途検討 (今回スコープ外) |
| Autopilot Cluster Mgmt Fee (after free credit) | ~¥6,000 | 削減不可 |
| Cloud Monitoring Metric Volume | ~¥1,800 | **本 change で対応** |
| Cloud SQL Regional Micro | ~¥2,600 | **本 change で対応** |
| Global LB Forwarding Rule | ~¥2,400 | 構成変更が必要 (今回スコープ外) |
| Autopilot Spot Pod + 周辺 | ~¥3,000 | **本 change で pod 数削減** |

調査自体は GCP Billing Console の CSV export と Cloud Monitoring API 直叩きで完結したが、**BigQuery Billing Export が無効だったため日次の SKU 別分解ができず**、May 23 の cost spike (¥3,300/日) の原因を確定できなかった。再発時に SQL で即診断できる基盤を恒久整備する判断。

現状の構成:
- otel-collector: `googlecloud` exporter に `processors: [batch]` のみ。filter 未設定で全 metric が流れる。
- Argo CD prod overlay: `argocd-server: 2 replicas`, image-updater / notifications / applicationset が default-on。
- Cloud SQL prod: `db-f1-micro`, `availabilityType: REGIONAL`, PSC 接続。
- BigQuery: prod project に dataset 無し、billing export も未設定。

## Goals / Non-Goals

**Goals:**
- otel-collector の filter で Cloud Monitoring metric ingest を 45 MiB/月 → ~0.3 MiB/月 に削減 (現課金 ¥1,800/月の解消 + 将来 prod scale-up 時の free tier 突破防御)。
- Argo CD prod overlay の pod 数を 8 → 5 に削減(image-updater-controller と applicationset-controller を `replicas: 0`、argocd-server を 2 → 1。notifications-controller は active subscription のため維持)。
- Cloud SQL prod を ZONAL 化して HA レプリカ分を解放 (¥1,000/月削減)。
- BQ billing export 基盤を Pulumi 管理化し、コスト調査を SQL で完結できる状態にする。
- 上記 4 つの作業を、安全な順序 (otel → Argo CD → BQ → Cloud SQL) で段階的に適用できる単一 change としてまとめる。

**Non-Goals:**
- Gemini API のコスト最適化 (prompt 設計改善、model 切り替え、grounding 削減)。月額の最大コストではあるがビジネスロジック改修が必要で本 change には含めない。
- Global LB → Regional LB への移行。Cloudflare TLS 終端構成の見直しが必要で別 change。
- concert-discovery の prompt 設計改善 (May 23 spike の根本原因かもしれないが、本 change はインフラ層の最適化に絞る)。
- 過去の dev 残債コストの遡及精算。dev cluster 削除 (5/18) で自然消滅済み。
- Cloud Monitoring SLO 用 metric の追加・dashboard 整備。

## Decisions

### Decision 1: otel-collector filter は OpenTelemetry Collector の `filter` processor で実装する

OTLP 受信後の pipeline に挿入する processor として、OpenTelemetry Collector 標準の `filter` processor を選択する。

**選択肢:**
- **A. `filter` processor (採用)**: metric name を正規表現または完全一致で drop。設定が宣言的で読みやすい。
- B. `transform` processor: より高機能だが、metric drop には overkill。OTEL Collector の維持コスト増。
- C. backend (otelconnect / otelhttp) 側で計装を止める: 根本的だがソース変更が広範に及ぶ。Go コード修正が必要で revert も重い。

**決定理由:** filter processor は YAML の宣言だけで完結し、否定的判断 (「これは出さない」) を一箇所に集約できる。otel-collector の再起動だけで反映され、backend デプロイ不要。将来 SLO 用に `rpc.server.duration` を復活させる時も filter ルールを 1 行変えるだけ。

**Drop ルール:**
```yaml
processors:
  filter/drop_workload_noise:
    metrics:
      exclude:
        match_type: regexp
        metric_names:
          - rpc\.server\..*           # 5 metric (duration, request.size, response.size, requests_per_rpc, responses_per_rpc)
          - http\.client\..*          # 2 metric (request.duration, request.body.size)
```

**Keep されるもの (明示的に列挙しないが filter 通過):**
- `concert.search.count` (business KPI, counter)
- `db.pool.active_connections` (gauge)
- `db.pool.idle_connections` (gauge)

**Service pipeline 変更:**
```yaml
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [filter/drop_workload_noise, batch]
      exporters: [googlecloud]
```

`filter` を `batch` の **前** に置くことで、drop 対象を batch 集約前に捨てる (batch を経由してから捨てる無駄を回避)。

### Decision 2: Argo CD の不要 pod 削減は base ではなく overlays/prod で patch する

prod overlay 限定の disable を行い、dev では現状動作を維持する。

**選択肢:**
- A. base/kustomization.yaml で完全に削除: dev も含めて全環境で disable される。dev の image auto-update が止まる。
- **B. overlays/prod/ で patch で 0 replicas にする (採用)**: dev 影響なし。base のリソース定義は残す。
- C. helm values の `enabled: false`: Argo CD は upstream Helm chart 経由でないため非対応。

**決定理由:** prod の semver pin 運用 (#274) は prod のみの制約。dev は image-updater による latest 追従が現役で必要。dev/prod の対称性を保ったまま prod のみ pod 数を減らせるのが Kustomize patch アプローチ。

**実装方針:**
```yaml
# k8s/namespaces/argocd/overlays/prod/disable-image-updater-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-image-updater-controller
spec:
  replicas: 0
---
# 同様に notifications-controller, applicationset-controller も replicas: 0 にする
# (未使用なら。tasks.md の事前確認で判断)
```

argocd-server の `replicas: 2 → 1` も同じ overlay の strategic merge patch で実施。

### Decision 3: Cloud SQL availability 切り替えは Pulumi 経由、staged rollout は行わない

Cloud SQL の `availabilityType` 変更は Pulumi で宣言的に行う。

**選択肢:**
- A. `gcloud sql instances patch` で手動切り替え: 即時反映だが Pulumi state とドリフトする。次の `pulumi preview` で REGIONAL に戻されるリスク。
- **B. Pulumi コード変更 + `pulumi up` (採用)**: state と実態が一致。レビュー履歴が残る。
- C. 段階的 (replica 削除 → primary 移行): Cloud SQL の HA は単一の `availabilityType` フラグで両者切り替わるため段階化不可。

**決定理由:** Pulumi 一元管理が破綻しない。`postgres.ts` で `availabilityType` を環境別に分岐させるか、`Pulumi.prod.yaml` 経由で config 化する。

**実装方針:**
```typescript
// postgres.ts または環境設定
settings: {
  availabilityType: environment === 'prod-ha' ? 'REGIONAL' : 'ZONAL',
  // または config key で:
  // availabilityType: cfg.get('postgres.availabilityType') ?? 'ZONAL',
}
```

「将来 REGIONAL に戻したくなった時」を考慮し、config key で切り替え可能にする実装を推奨する。新しい環境タイプを増やすより config flag のほうが軽い。

### Decision 4: BigQuery Billing Export は Pulumi で dataset + IAM のみ管理、export 有効化操作は runbook 化

Billing Export の有効化 API/CLI に Pulumi resource が存在しないため、Pulumi で provision できる範囲を最大化し、最後の手動ステップを runbook で固定化する。

**選択肢:**
- A. 完全に手動 (Console のみ): 既存運用と同じ。コード化のメリット無し。
- **B. dataset + IAM を Pulumi、export 有効化は runbook 手動 (採用)**: 99% Pulumi 化、最終ステップだけ Console。
- C. Cloud Billing API を直接叩く Pulumi Dynamic Provider を書く: 過剰実装。billing export の有効化は 1 回しか発生しないオペレーション。

**決定理由:** Pulumi GCP provider に `gcp.billing.AccountIamMember` はあるが、「billing account → BQ dataset への export」を直接表現する resource は無い (2025-05 時点)。dataset と IAM 権限を Pulumi で揃えれば、Console での export 有効化は dataset を選ぶだけの 30 秒操作になる。

**Provision するもの:**
```typescript
// src/gcp/components/billing-export.ts (新規)
new gcp.bigquery.Dataset('billing-export', {
  datasetId: 'billing_export',
  location: 'asia-northeast1',
  description: 'GCP Billing Export — standard + detailed usage cost',
  project: 'liverty-music-prod',
})

new gcp.bigquery.DatasetIamMember('billing-export-svc', {
  datasetId: 'billing_export',
  role: 'roles/bigquery.dataEditor',
  member: 'serviceAccount:cloud-billing-export@system.gserviceaccount.com',
  // ↑ 正確なサービスアカウント名は GCP docs で確認、または billing-account の serviceConfig から取得
})
```

**runbook (新規):** `docs/runbooks/enable-billing-export.md` に以下を記載:
1. `pulumi up` で dataset + IAM が provision されたことを確認
2. Console → Billing → Billing export → BigQuery export
3. Standard usage cost を Edit → project=liverty-music-prod, dataset=billing_export → Save
4. Detailed usage cost も同様に有効化
5. (任意) Pricing export も同 dataset に向ける
6. 24h 後に `bq ls liverty-music-prod:billing_export` でテーブル生成を確認
7. テーブルが現れない場合は IAM 権限を再確認

### Decision 5: 適用順序は「リスクが小さい順」で otel → Argo CD → BQ → Cloud SQL

各サブタスクは独立しているが、依存関係はなくても適用時のリスク (= 影響範囲 × 復旧難度) が異なる。

**順序:**
1. **otel filter** (最低リスク): collector 再起動のみ。metric が一時欠損するだけで他に影響なし。失敗しても`kubectl rollout undo` で即復旧。
2. **Argo CD pod 削減** (低リスク): replicas 0 化は revert 容易。image-updater は disable しても sync 自体は動く。
3. **BQ Export 基盤** (低リスク): 新規リソース作成のみ、既存に影響しない。失敗しても削除して再 provision。
4. **Cloud SQL ZONAL 化** (中リスク): 数分のダウンタイム発生。事前にトラフィック確認、メンテナンス時間帯で実施。

各タスクの間に 1 日程度の観察期間を置く運用も可能 (連続適用必須ではない)。

## Risks / Trade-offs

- **Risk:** otel filter で必要な metric を誤って drop する
  → **Mitigation:** filter の正規表現を `rpc.server.*` と `http.client.*` に限定し、他の workload metric (db.pool.*, concert.search.count) は影響を受けない。Cloud Monitoring の `bytes_ingested` で適用前後の差分を確認する。

- **Risk:** Argo CD image-updater を disable した直後に dev の運用が混乱する
  → **Mitigation:** disable は overlays/prod でのみ実施。dev overlay は触らない。kustomize dry-run で確認してからマージ。

- **Risk:** Cloud SQL ZONAL 化中の数分ダウンタイムでユーザー影響
  → **Mitigation:** Cloudflare の前段で 503 を返す or maintenance ページに切り替え。Pulumi の preview で変更内容を確認後、低トラフィック時間帯 (深夜 JST) に実施。トラフィック規模が小さい launch 直後である今が実施好機。

- **Risk:** BQ Billing Export の IAM 権限不足で provision 後も export が始まらない
  → **Mitigation:** runbook の検証ステップ (24h 後の `bq ls` 確認) を必須化。失敗時は GCP docs / Cloud Logging audit trail で実際の writer SA を特定し、`cloud-billing-export@system.gserviceaccount.com` 以外の SA であれば IAM binding を差し替える。

- **Trade-off:** ZONAL 化で zonal failover の自動冗長性を失う
  → 将来トラフィック増加で SLA が厳しくなったら config key を `REGIONAL` に戻すだけで HA 復活可能。今のコスト > SLA リスクの判断。

- **Trade-off:** otel filter で将来 SLO 用 latency histogram を使いたくなった場合に re-enable コストが発生
  → filter は YAML 1 行で除外でき、PR 1 件で復活可能。Cloud Monitoring 側に metric definition が残るので途絶期間中の欠損はあるが運用継続には支障なし。

## Migration Plan

各タスクは独立して revert 可能。順序通り適用すれば総ダウンタイムは Cloud SQL 切り替え時の数分のみ。

1. otel filter PR → review → merge → ArgoCD sync → 24h 観察
2. Argo CD pod 削減 PR → review → merge → ArgoCD sync → image-updater 停止確認
3. BQ Billing Export Pulumi PR → review → merge → `pulumi up` prod → Console で export 有効化 → 24h 後 `bq ls` で確認
4. Cloud SQL ZONAL PR → review → merge → Pulumi preview → メンテナンス時間帯に `pulumi up` prod → DB 接続性確認

Rollback: 各 PR を revert + 再 ArgoCD sync / `pulumi up` で原状復帰。

## Open Questions

- **Q1:** Argo CD の `notifications-controller` と `applicationset-controller` は実運用で使用されているか? 未使用なら disable、使用中なら維持。tasks.md の 1st step で確認する。
- **Q2:** Cloud SQL config key 化 (Decision 3) の名前。`postgres.availabilityType` (string) と `postgres.haEnabled` (boolean) のどちらが好みか。前者は GCP 用語そのもの、後者は意図が読みやすい。tasks.md で実装時に決定する。
- **Q3 (resolved):** BQ Billing Export の billing service account 名は GCP 公式 docs で確認済み。`cloud-billing-export@system.gserviceaccount.com` を Pulumi 実装で採用。GCP が将来 principal 名を変えた場合は runbook の troubleshooting セクションで Cloud Logging audit trail から実際の SA を特定する手順を整備済み。
