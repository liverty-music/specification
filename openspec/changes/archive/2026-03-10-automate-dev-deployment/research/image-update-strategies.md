# デプロイメント戦略の提案

## 要件まとめ

```
┌─────────────────────────────────────────────────────────┐
│                   REQUIREMENTS                          │
├─────────────────────────────────────────────────────────┤
│ • dev: 1日に複数回のマージ                              │
│ • dev: 自動デプロイ希望                                 │
│ • dev: latest タグ使用（commit history 汚染回避）      │
│ • prod: GitHub Release による手動トリガー               │
│ • prod: Semantic versioning                             │
│ • Team: Solo developer                                  │
│ • Environments: dev, prod のみ                          │
└─────────────────────────────────────────────────────────┘
```

---

## オプション 1: ArgoCD Image Updater (推奨 ⭐)

### アーキテクチャ

```
Backend Repo (main branch)
    │
    ▼ PR merged
┌───────────────────────────────────┐
│ GitHub Actions                    │
├───────────────────────────────────┤
│ 1. Build image                    │
│ 2. Push to GAR                    │
│    - tag: latest                  │
│    - tag: ${GITHUB_SHA}           │
└─────────────┬─────────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │   GAR (Registry)        │
    │   • latest (updated)    │
    │   • e84baf2             │
    │   • 3f2a1b9             │
    └───────┬─────────────────┘
            │
            │ polls every 2min
            │
            ▼
    ┌─────────────────────────────────────┐
    │  ArgoCD Image Updater (dev only)    │
    ├─────────────────────────────────────┤
    │ • Watches GAR for `latest` tag      │
    │ • Detects digest change             │
    │ • Updates kustomization (dev)       │
    │ • Commits to git automatically      │
    └─────────────┬───────────────────────┘
                  │
                  ▼
    ┌───────────────────────────────────────┐
    │  cloud-provisioning repo              │
    ├───────────────────────────────────────┤
    │  dev overlay:                         │
    │    newTag: latest                     │
    │    ↓ auto-updated by Image Updater   │
    │                                       │
    │  prod overlay:                        │
    │    newTag: v1.2.3                     │
    │    ↓ manual update on release        │
    └─────────────┬─────────────────────────┘
                  │
                  ▼
    ┌───────────────────────────────────────┐
    │  ArgoCD (auto-sync enabled)           │
    ├───────────────────────────────────────┤
    │  dev:  syncs automatically            │
    │  prod: syncs manually after release   │
    └───────────────────────────────────────┘
```

### 設定方法

#### 1. ArgoCD Image Updater をインストール

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

#### 2. dev 環境の ArgoCD Application に annotation 追加

```yaml
# k8s/argocd-apps/dev/backend.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: backend
  annotations:
    # ArgoCD Image Updater の設定
    argocd-image-updater.argoproj.io/image-list: server=asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
    argocd-image-updater.argoproj.io/server.update-strategy: latest
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
spec:
  source:
    path: k8s/namespaces/backend/overlays/dev
  # ... rest of config
```

#### 3. prod 環境は従来通り

```yaml
# k8s/argocd-apps/prod/backend.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: backend
  # Image Updater の annotation なし
spec:
  source:
    path: k8s/namespaces/backend/overlays/prod
  syncPolicy:
    automated:
      prune: false  # prod は自動 sync しない
      selfHeal: false
```

#### 4. Kustomization の構造

```
k8s/namespaces/backend/
├── base/
│   └── server/
│       ├── kustomization.yaml
│       │   # 共通設定、image name のみ
│       │   images:
│       │   - name: server
│       │     newName: asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
│       │     # newTag は overlay で指定
│       └── deployment.yaml
├── overlays/
│   ├── dev/
│   │   └── kustomization.yaml
│   │       # dev 固有設定
│   │       images:
│   │       - name: server
│   │         newTag: latest  # Image Updater が自動更新
│   │       patches:
│   │       - patch: |-
│   │           - op: replace
│   │             path: /spec/replicas
│   │             value: 1
│   └── prod/
│       └── kustomization.yaml
│           # prod 固有設定
│           images:
│           - name: server
│             newTag: v1.2.3  # 手動で更新
│           patches:
│           - patch: |-
│               - op: replace
│                 path: /spec/replicas
│                 value: 2
```

### GitHub Release → prod デプロイのワークフロー

```bash
# 1. GitHub で Release 作成 (v1.2.3)
gh release create v1.2.3 --notes "Release notes here"

# 2. cloud-provisioning repo で prod overlay 更新
cd k8s/namespaces/backend/overlays/prod
# kustomization.yaml の newTag を v1.2.3 に変更

# 3. Commit & Push
git add kustomization.yaml
git commit -m "release: deploy backend v1.2.3 to prod"
git push

# 4. ArgoCD で手動 sync
argocd app sync backend-prod
```

### メリット

✅ **dev: 完全自動化**
- main にマージするだけで自動デプロイ
- commit history 汚染なし
- Image Updater が digest を監視するので `latest` でも安全

✅ **prod: 明確なリリースフロー**
- GitHub Release でバージョン管理
- 手動トリガーで安心
- ロールバックが容易 (tag を戻すだけ)

✅ **Solo developer に最適**
- セットアップ後はほぼメンテナンス不要
- ArgoCD エコシステム内で完結
- 追加の CI/CD 設定不要

### デメリット

⚠️ **初回セットアップが必要**
- ArgoCD Image Updater のインストール (10分)
- Git write-back 用の権限設定 (5分)

⚠️ **Image Updater の commit が増える**
- でも、ファイル変更は最小限 (newTag の digest のみ)
- commit message は自動生成
- main への直接コミットなので PR 不要

---

## オプション 2: kubectl rollout restart (最もシンプル ⭐⭐)

### アーキテクチャ

```
Backend Repo (main branch)
    │
    ▼ PR merged
┌───────────────────────────────────┐
│ GitHub Actions                    │
├───────────────────────────────────┤
│ 1. Build image                    │
│ 2. Push to GAR                    │
│    - tag: latest                  │
│    - tag: ${GITHUB_SHA}           │
│ 3. Trigger rollout restart (dev)  │
│    kubectl rollout restart        │
└───────────────────────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │   GAR (Registry)        │
    │   • latest (updated)    │
    └─────────────────────────┘
              │
              │ kubectl pulls new image
              │
              ▼
    ┌─────────────────────────────────┐
    │  GKE dev cluster                │
    │  • Rolling update triggered     │
    │  • Pulls latest image           │
    │  • No manifest change needed    │
    └─────────────────────────────────┘
```

### 設定方法

#### 1. Backend の GitHub Actions に追加

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for GAR
        run: gcloud auth configure-docker asia-northeast2-docker.pkg.dev

      - name: Build and push
        run: |
          docker build -t asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:latest .
          docker tag asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:latest \
                     asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:${{ github.sha }}
          docker push asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:latest
          docker push asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:${{ github.sha }}

      # ⭐ dev 環境への自動デプロイ
      - name: Deploy to dev
        run: |
          gcloud container clusters get-credentials osaka-cluster --region asia-northeast2
          kubectl rollout restart deployment/server-deployment -n backend
          kubectl rollout status deployment/server-deployment -n backend --timeout=5m
```

#### 2. Kustomization は latest 固定

```yaml
# k8s/namespaces/backend/overlays/dev/kustomization.yaml
images:
- name: server
  newTag: latest  # 固定、変更不要

# k8s/namespaces/backend/overlays/prod/kustomization.yaml
images:
- name: server
  newTag: v1.2.3  # Release 時に手動更新
```

#### 3. ImagePullPolicy 設定

```yaml
# k8s/namespaces/backend/base/server/deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: server
        image: server
        imagePullPolicy: Always  # 重要: latest タグの場合は必須
```

### GitHub Release → prod デプロイのワークフロー

```bash
# 1. GitHub で Release 作成 (v1.2.3)
gh release create v1.2.3 --notes "Release notes"

# 2. Backend の GitHub Actions が v1.2.3 タグをビルド & プッシュ
# (release 時のワークフロー追加が必要)

# 3. cloud-provisioning repo で prod overlay 更新
cd k8s/namespaces/backend/overlays/prod
# kustomization.yaml の newTag を v1.2.3 に変更

# 4. Commit & Push
git commit -am "release: deploy backend v1.2.3 to prod"
git push

# 5. ArgoCD が自動 sync (または手動 sync)
```

### メリット

✅ **最もシンプル**
- 追加コンポーネント不要
- GitHub Actions だけで完結
- 理解しやすい

✅ **commit history 汚染ゼロ**
- cloud-provisioning repo への commit 不要 (dev)
- kubectl が直接 Pod を再起動

✅ **即座にデプロイ**
- rollout restart は数秒で完了
- Image Updater のポーリング待ちなし

### デメリット

⚠️ **GitOps の原則から逸脱**
- Git が唯一の真実の源ではない
- kubectl コマンドで直接操作

⚠️ **ArgoCD の管理外**
- ArgoCD は Out of Sync 状態になる
- でも、実害はない（dev 環境のみ）

⚠️ **latest タグのリスク**
- digest が変わらないと古いイメージが使われる可能性
- imagePullPolicy: Always で軽減

---

## オプション 3: Digest-based Update (ハイブリッド ⭐⭐⭐)

### アーキテクチャ

```
Backend Repo (main branch)
    │
    ▼ PR merged
┌──────────────────────────────────────────┐
│ GitHub Actions                           │
├──────────────────────────────────────────┤
│ 1. Build & Push                          │
│    - tag: latest                         │
│    - tag: ${GITHUB_SHA}                  │
│ 2. Get image digest                      │
│ 3. Update cloud-provisioning (dev)       │
│    - Use digest instead of tag           │
│    - No commit history pollution         │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│ cloud-provisioning repo                  │
├──────────────────────────────────────────┤
│ dev overlay:                             │
│   newName: ..../server@sha256:abc123...  │
│   ↑ digest で指定（完全に一意）         │
│                                          │
│ prod overlay:                            │
│   newTag: v1.2.3                         │
│   ↑ semantic version                     │
└──────────────────────────────────────────┘
```

### 設定方法

#### 1. Backend の GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy-dev:
    runs-on: ubuntu-latest
    steps:
      # ... build & push steps ...

      - name: Get image digest
        id: digest
        run: |
          DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' \
                   asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server:latest)
          echo "digest=$DIGEST" >> $GITHUB_OUTPUT

      - name: Update dev kustomization
        env:
          GH_TOKEN: ${{ secrets.GH_PAT }}
        run: |
          # cloud-provisioning repo をチェックアウト
          git clone https://github.com/liverty-music/cloud-provisioning.git
          cd cloud-provisioning

          # yq で digest を更新
          yq -i '.images[0].newName = "${{ steps.digest.outputs.digest }}"' \
            k8s/namespaces/backend/overlays/dev/kustomization.yaml

          # Commit (squash して履歴を圧縮)
          git add k8s/namespaces/backend/overlays/dev/kustomization.yaml
          git commit -m "chore(dev): update backend image [skip ci]"
          git push
```

#### 2. Commit history の圧縮スクリプト（週1回実行）

```bash
#!/bin/bash
# scripts/squash-dev-updates.sh

# 過去7日間の "chore(dev): update backend image" コミットを1つに squash
git log --oneline --since="7 days ago" --grep="chore(dev): update backend image" \
  | wc -l

# 実際の squash は手動または cron で実行
```

### メリット

✅ **Digest の一意性**
- Tag ではなく digest で指定
- キャッシュミスなし
- 完全に一意なイメージ識別

✅ **GitOps 準拠**
- Git が唯一の真実の源
- ArgoCD が正しく管理

✅ **Commit 圧縮可能**
- 定期的に squash して履歴を整理
- または [skip ci] で CI を回避

### デメリット

⚠️ **Commit は発生する**
- でも digest なので tag より情報量が多い
- Squash で履歴を整理可能

⚠️ **GitHub PAT が必要**
- Personal Access Token の管理
- セキュリティ考慮が必要

---

## 比較表

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          COMPARISON TABLE                                │
├────────────────┬─────────────┬─────────────┬─────────────┬──────────────┤
│                │ Option 1    │ Option 2    │ Option 3    │ Manual       │
│                │ Image       │ kubectl     │ Digest-     │ (current)    │
│                │ Updater     │ rollout     │ based       │              │
├────────────────┼─────────────┼─────────────┼─────────────┼──────────────┤
│ Setup Time     │ 15 min      │ 10 min ✓    │ 20 min      │ 0 min ✓✓     │
│ Complexity     │ Medium      │ Low ✓       │ Medium      │ Low ✓✓       │
│ GitOps         │ Yes ✓       │ No          │ Yes ✓       │ Yes ✓        │
│ Automation     │ Full ✓      │ Full ✓      │ Full ✓      │ Manual       │
│ Commit Hist    │ Auto commits│ Clean ✓✓    │ Auto commits│ Clean ✓      │
│ ArgoCD Compat  │ Native ✓✓   │ Out of Sync │ Native ✓✓   │ Native ✓✓    │
│ Rollback       │ Easy ✓      │ Manual      │ Easy ✓      │ Easy ✓       │
│ Image Safety   │ Digest ✓✓   │ Tag cache?  │ Digest ✓✓   │ Depends      │
│ Maintenance    │ Low ✓       │ Low ✓       │ Medium      │ High         │
│ Solo Dev       │ Good ✓      │ Best ✓✓     │ Good ✓      │ OK           │
├────────────────┼─────────────┼─────────────┼─────────────┼──────────────┤
│ RECOMMENDATION │ ⭐⭐⭐      │ ⭐⭐⭐⭐    │ ⭐⭐        │ ⭐           │
│                │ Production  │ Pragmatic   │ Purist      │ MVP only     │
│                │ Ready       │ Quick start │ GitOps      │              │
└────────────────┴─────────────┴─────────────┴─────────────┴──────────────┘
```

---

## 私の推奨

### 短期（今すぐ）: **Option 2 - kubectl rollout restart**

理由:
1. **10分で完成** - 今日から使える
2. **Solo developer に最適** - 余計な複雑さなし
3. **Commit history クリーン** - cloud-provisioning は dev では触らない
4. **十分に安全** - imagePullPolicy: Always で対応

### 長期（スケール時）: **Option 1 - ArgoCD Image Updater**

理由:
1. **チームが増えたら** - GitOps 準拠で安心
2. **複数サービスに対応** - スケールしやすい
3. **ArgoCD エコシステム** - 一貫した管理

---

## 実装プラン（Option 2 採用の場合）

### Phase 1: dev 自動デプロイ（今日）

```bash
# 1. backend/.github/workflows/deploy.yml に rollout restart 追加
# 2. GCP Service Account に GKE 権限追加
# 3. test push して動作確認
```

### Phase 2: prod リリースフロー（次週）

```bash
# 1. backend/.github/workflows/release.yml 作成
#    - GitHub Release 作成時にトリガー
#    - v{version} タグでイメージをビルド
# 2. cloud-provisioning の prod overlay を手動更新
# 3. ArgoCD で手動 sync
```

### Phase 3: Monitoring（継続）

```bash
# 1. ArgoCD で dev のデプロイ状況を監視
# 2. GKE ログで異常を検知
# 3. 問題があれば Option 1 に移行検討
```

---

## 次のステップ

Option 2 で進める場合、以下を実装しましょうか？

1. ✅ backend/.github/workflows/deploy.yml の更新
2. ✅ GCP Service Account 権限設定
3. ✅ deployment.yaml に imagePullPolicy: Always 追加
4. ✅ Test push して動作確認

どう思いますか？
