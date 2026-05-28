## 1. otel-collector filter (lowest risk, do first)

- [x] 1.1 `cloud-provisioning/k8s/namespaces/otel-collector/base/configmap.yaml` に `filter/drop_workload_noise` processor を追加(`rpc.server.*` と `http.client.*` を regexp で exclude)
- [x] 1.2 同 ConfigMap の `service.pipelines.metrics.processors` を `[filter/drop_workload_noise, batch]` の順に更新
- [x] 1.3 ConfigMap に filter ルールの意図と保持メトリクス一覧を説明するコメントブロックを追加
- [x] 1.4 `kubectl kustomize k8s/namespaces/otel-collector/overlays/prod` で dry-run し、ConfigMap が正しくレンダリングされることを確認
- [ ] 1.5 PR を作成、レビュー、マージ。ArgoCD が prod cluster の otel-collector Deployment を sync するのを待つ
- [ ] 1.6 適用後 24h の `monitoring.googleapis.com/billing/bytes_ingested` (prod project) を確認し、日次 ingest が 1 MiB/日未満に落ちていることを検証
- [ ] 1.7 業務メトリクス (`concert.search.count`, `db.pool.active_connections`, `db.pool.idle_connections`) が Cloud Monitoring に依然として記録されていることを確認

## 2. Argo CD prod overlay の Pod 削減

- [x] 2.1 prod cluster で `argocd-notifications-controller` と `argocd-applicationset-controller` の使用状況を確認(notification ルール定義の有無、ApplicationSet リソースの有無)
- [x] 2.2 未使用と確認できた controller を 2.4 の対象に含めるか判断 — notifications-controller は active subscription があるため維持、applicationset-controller のみ disable
- [x] 2.3 `k8s/namespaces/argocd/overlays/prod/kustomization.yaml` に `argocd-image-updater-controller` の `replicas: 0` inline patch を追加(別ファイル化はせず簡潔に)
- [x] 2.4 同 kustomization.yaml に `argocd-applicationset-controller` の `replicas: 0` patch を追加(notifications-controller は維持)
- [x] 2.5 既存の `argocd-server` patch を `replicas: 2 → 1` に変更
- [x] 2.6 各 patch ブロックに「なぜ replicas: 0 / 1 か」のコメントを追加
- [x] 2.7 `k8s/namespaces/argocd/overlays/prod/kustomization.yaml` に新規 patch を登録(同 file 内 inline で完結)
- [x] 2.8 ローカル kustomize 環境の Helm v4 / v3 互換性問題で `kubectl kustomize --enable-helm` がローカル失敗。YAML 構文 + patch 構造は `python yaml.safe_load` でチェック済み(CI でレンダリング検証)
- [x] 2.9 dev overlay は触っていないことを確認(git diff で overlays/prod のみ変更)
- [ ] 2.10 PR を作成、レビュー、マージ
- [ ] 2.11 ArgoCD sync 後、`kubectl get pods -n argocd` で対象 Pod が 0 または 1 になっていることを確認
- [ ] 2.12 dev cluster の image-updater が引き続き auto-update 動作していることを確認(dev で次回 image push 時のログを確認)

## 3. BigQuery Billing Export 基盤の Pulumi 化

- [x] 3.1 `cloud-provisioning/src/gcp/components/billing-export.ts` を新規作成。`gcp.bigquery.Dataset` で `billing_export` (asia-northeast1, project liverty-music-prod) を定義
- [x] 3.2 同コンポーネントで `gcp.bigquery.DatasetIamMember` を定義し、`cloud-billing-export@system.gserviceaccount.com` に `roles/bigquery.dataEditor` を付与
- [x] 3.3 `src/gcp/index.ts` の `Gcp` クラスで `environment === 'prod'` ガード付きで `BillingExportComponent` をインスタンス化
- [x] 3.4 `bigquery.googleapis.com` を `GoogleApis` 型に追加(`services/api.ts`)
- [ ] 3.5 `pulumi preview --stack prod` で diff を確認(新規 dataset + IAM 2 リソースのみ)
- [ ] 3.6 PR を作成、レビュー、マージ
- [ ] 3.7 Pulumi Cloud Console から prod stack の `pulumi up` を手動 trigger
- [ ] 3.8 `bq --project_id=liverty-music-prod ls billing_export` で dataset の存在を確認
- [x] 3.9 `docs/runbooks/enable-billing-export.md` を新規作成。Console 操作手順(Billing → Billing export → BigQuery export → Standard + Detailed 有効化)を記載
- [x] 3.10 同 runbook に検証ステップ(24h 後の `bq ls liverty-music-prod:billing_export` でテーブル生成確認)と例 SQL(日次 SKU breakdown、per-namespace GKE Pod cost、cost-spike 特定)を記載
- [ ] 3.11 Console で Standard usage cost export と Detailed usage cost export を有効化(runbook 通り)
- [ ] 3.12 24h 後に `bq ls liverty-music-prod:billing_export` でテーブルが作成されていることを確認、できていなければ IAM 権限を再チェック

## 4. Cloud SQL prod を REGIONAL → ZONAL に変更(highest risk, do last)

- [x] 4.1 `postgres.ts` で `availabilityType` を `PostgresComponentArgs` 経由で受け取れるよう変更。`src/index.ts` で `liverty-music:postgresAvailabilityType` config key から読み取り(default `ZONAL`、型チェック付き)、`Gcp` 経由で `PostgresComponent` に渡す
- [x] 4.2 `Pulumi.prod.yaml` に `liverty-music:postgresAvailabilityType: ZONAL` を明示設定(コメントで運用ポリシー説明)
- [ ] 4.3 `pulumi preview --stack prod` で diff を確認(`availabilityType: REGIONAL → ZONAL` のみが変更項目であること)
- [ ] 4.4 PR を作成、レビュー、マージ
- [ ] 4.5 メンテナンス時間帯(JST 深夜、低トラフィック時)を設定
- [ ] 4.6 (任意)Cloudflare で maintenance ページに切り替え、または DB 接続が必要な API endpoint で 503 を返す事前準備
- [ ] 4.7 Pulumi Cloud Console から `pulumi up --stack prod` を手動 trigger
- [ ] 4.8 切り替え完了後、`gcloud sql instances describe postgres-osaka --project=liverty-music-prod --format="value(settings.availabilityType,state)"` で `ZONAL, RUNNABLE` を確認
- [ ] 4.9 backend Pod から DB 接続が回復していることを確認(pod logs に errors が無い、`SELECT 1` が通る)
- [ ] 4.10 (該当する場合)maintenance モードを解除し、トラフィックを通常運用に戻す
- [ ] 4.11 完了後の月次コスト効果を翌月の billing で確認(Cloud SQL Regional Micro SKU の `Subtotal` が大幅減 → Zonal Micro SKU 側に移行)

## 5. 完了確認 & ドキュメント

- [ ] 5.1 翌請求月の billing CSV で Cloud Monitoring `Metric Volume`, Argo CD 経由の `Autopilot Spot Pod` 合計, Cloud SQL `Regional Micro` の SKU 単位コストの減少を確認
- [ ] 5.2 削減実績を記録(目標 ¥3,250-3,600/月 ≈ otel filter ¥1,800-2,000 + Argo CD ¥150-300 + Cloud SQL ¥1,300、実績は CSV 差分から計算)
- [ ] 5.3 OpenSpec change を `/opsx:verify` で検証
- [ ] 5.4 `/opsx:archive` で change を archive
