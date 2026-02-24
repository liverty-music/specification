# デプロイメント戦略 2026 年版アップデート

## 🆕 新発見: Flux CD のビルトイン Image Automation

### 重要な発見

[Flux CD vs. Argo CD 比較](https://aws.plainenglish.io/argocd-vs-flux-in-2025-the-gitops-war-is-over-and-you-won-d22e084929a5)によると、**Flux CD はイメージ自動化が組み込み機能**として提供されています。これは ArgoCD Image Updater（外部プラグイン）よりもシンプルです。

```
┌──────────────────────────────────────────────────────┐
│         Flux CD vs ArgoCD (Image Automation)         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Flux CD:                                            │
│  ✅ Built-in image automation                       │
│  ✅ Image Reflector Controller (標準)               │
│  ✅ Image Automation Controller (標準)              │
│                                                      │
│  ArgoCD:                                             │
│  ⚠️  External Image Updater required                │
│  ⚠️  Separate installation needed                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## オプション 4: Flux CD Image Automation (新提案 ⭐⭐⭐)

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
    └───────┬─────────────────┘
            │
            │ watches registry
            │
            ▼
    ┌──────────────────────────────────────┐
    │  Flux Image Reflector Controller     │
    │  (ビルトイン機能)                    │
    ├──────────────────────────────────────┤
    │ • GAR の latest タグを監視           │
    │ • Digest 変更を検知                  │
    │ • ImagePolicy で更新ルール定義       │
    └─────────────┬────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────┐
    │  Flux Image Automation Controller    │
    │  (ビルトイン機能)                    │
    ├──────────────────────────────────────┤
    │ • cloud-provisioning repo を更新     │
    │ • Git commit & push 自動             │
    │ • dev のみ自動、prod は手動          │
    └─────────────┬────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────┐
    │  cloud-provisioning repo             │
    ├──────────────────────────────────────┤
    │  dev overlay: 自動更新 ✓             │
    │  prod overlay: 手動更新 ✓            │
    └─────────────┬────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────┐
    │  Flux Kustomization Controller       │
    │  自動 sync & deploy                  │
    └──────────────────────────────────────┘
```

### 設定方法

#### 1. Flux CLI インストール

```bash
curl -s https://fluxcd.io/install.sh | sudo bash
```

#### 2. Flux のブートストラップ（既存の ArgoCD と共存可能）

```bash
# Flux を特定の namespace にインストール（ArgoCD と共存）
flux install --namespace=flux-system

# または既存の ArgoCD を維持して Flux を追加インストール
kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml
```

#### 3. ImageRepository を作成（GAR を監視）

```yaml
# k8s/flux/image-repository.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: backend-server
  namespace: flux-system
spec:
  image: asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
  interval: 1m0s  # 1分ごとにレジストリをスキャン
```

#### 4. ImagePolicy を作成（更新ルール定義）

```yaml
# k8s/flux/image-policy.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: backend-server-policy
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: backend-server
  policy:
    semver:
      range: '>=1.0.0'  # prod: semantic versioning
  # または latest タグ用
  # policy:
  #   alphabetical:
  #     order: asc
```

#### 5. ImageUpdateAutomation を作成（Git への自動コミット）

```yaml
# k8s/flux/image-update-automation.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageUpdateAutomation
metadata:
  name: backend-dev-auto-update
  namespace: flux-system
spec:
  interval: 1m0s
  sourceRef:
    kind: GitRepository
    name: cloud-provisioning
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcdbot@users.noreply.github.com
        name: fluxcdbot
      messageTemplate: |
        chore(dev): auto-update backend image

        Automation name: {{ .AutomationObject }}

        Files:
        {{ range $filename, $_ := .Changed.FileChanges -}}
        - {{ $filename }}
        {{ end -}}

        Objects:
        {{ range $resource, $changes := .Changed.Objects -}}
        - {{ $resource.Kind }} {{ $resource.Name }}
          Changes:
        {{- range $_, $change := $changes }}
          - {{ $change.OldValue }} -> {{ $change.NewValue }}
        {{ end -}}
        {{ end -}}
    push:
      branch: main
  update:
    path: ./k8s/namespaces/backend/overlays/dev
    strategy: Setters  # kustomization の images を更新
```

#### 6. Kustomization にマーカー追加

```yaml
# k8s/namespaces/backend/overlays/dev/kustomization.yaml
images:
- name: server
  newName: asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
  newTag: latest # {"$imagepolicy": "flux-system:backend-server-policy"}
  # ↑ Flux がこのコメントを認識して自動更新
```

### メリット

✅ **ビルトイン機能**
- 外部プラグイン不要
- Flux のコア機能として提供
- メンテナンスが容易

✅ **ArgoCD と共存可能**
- Flux を Image Automation のみに使用
- ArgoCD は既存のまま維持
- 段階的な移行が可能

✅ **柔軟な更新ポリシー**
- Semver、regex、alphabetical など複数のポリシー
- dev は latest、prod は semver で使い分け可能

✅ **詳細な commit message**
- 何が変わったか自動で記録
- Audit trail が明確

### デメリット

⚠️ **新しいツールの導入**
- Flux の学習コスト
- でも、Image Automation だけなら学習範囲は狭い

⚠️ **ツールの混在**
- ArgoCD + Flux の2つ
- でも、役割分担が明確なら問題なし

---

## オプション 5: Kyverno Image Mutation (ポリシーベース)

### 概要

[Kyverno](https://kyverno.io/policies/other/update-image-tag/update-image-tag/) は Kubernetes-native なポリシーエンジンで、イメージタグの自動変換が可能です。

### アーキテクチャ

```
Pod が作成される際に Kyverno が介入
┌──────────────────────────────────────┐
│  kubectl apply -f deployment.yaml    │
│  image: server:latest                │
└────────────┬─────────────────────────┘
             │
             ▼ admission webhook
    ┌────────────────────────┐
    │  Kyverno Policy        │
    ├────────────────────────┤
    │ if tag == "latest":    │
    │   tag = get_digest()   │
    │   policy = Always      │
    └────────┬───────────────┘
             │
             ▼ mutated
┌──────────────────────────────────────────────┐
│  Deployed Pod                                │
│  image: server@sha256:abc123...             │
│  imagePullPolicy: Always                     │
└──────────────────────────────────────────────┘
```

### 設定例

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-imagepullpolicy-always
spec:
  rules:
  - name: add-imagepullpolicy
    match:
      any:
      - resources:
          kinds:
          - Pod
    mutate:
      patchStrategicMerge:
        spec:
          containers:
          - (name): "*"
            imagePullPolicy: Always
---
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: replace-image-tag-with-digest
spec:
  rules:
  - name: replace-tag-with-digest
    match:
      any:
      - resources:
          kinds:
          - Pod
    mutate:
      foreach:
      - list: "request.object.spec.containers"
        patchStrategicMerge:
          spec:
            containers:
            - name: "{{ element.name }}"
              image: "{{ images.containers.'{{element.name}}'.registry }}/{{ images.containers.'{{element.name}}'.path }}@{{ images.containers.'{{element.name}}'.digest }}"
```

### メリット

✅ **ランタイムでの自動変換**
- Manifest は latest のまま
- 実際のデプロイ時に digest に変換
- Git commit 不要

✅ **ポリシーベース**
- 一度設定すれば全リソースに適用
- 統一されたルール

### デメリット

⚠️ **可視性が低い**
- Git に記録されない
- 実際に何がデプロイされたか不明確

⚠️ **GitOps 原則から逸脱**
- Git が唯一の真実の源ではない

⚠️ **複雑性**
- Kyverno の学習コスト
- ポリシーのメンテナンス

---

## オプション 6: Argo Rollouts（プログレッシブデリバリー）

### 概要

[Argo Rollouts](https://argo-rollouts.readthedocs.io/) は Blue-Green や Canary デプロイメントを提供しますが、これは**デプロイ戦略**の話であり、**イメージ更新の自動化**とは別の話です。

ただし、dev 環境でのリスク軽減には有効:

```
┌────────────────────────────────────────────────────┐
│         Canary Deployment (dev 環境)               │
└────────────────────────────────────────────────────┘

Step 1: 10% traffic to new version
┌─────────┐  ┌─────────┐
│ v1 (90%)│  │v2 (10%) │
└─────────┘  └─────────┘

Step 2: Monitor metrics
         ↓
    ✅ Success → 100% v2
    ❌ Failure → Rollback to v1

Step 3: Gradual rollout
┌─────────┐
│v2 (100%)│
└─────────┘
```

### メリット

✅ **リスク軽減**
- 段階的なロールアウト
- 自動ロールバック

✅ **メトリクスベースの判断**
- Prometheus と連携
- エラー率が高ければ自動で止まる

### デメリット

⚠️ **イメージ更新の自動化ではない**
- 別途 Image Updater が必要
- デプロイ戦略のみを提供

⚠️ **複雑性増加**
- 新しい CRD (Rollout) の学習
- Prometheus 連携の設定

---

## 最新ベストプラクティス（2026年版）

### 1. imagePullPolicy の設定

[Kubernetes 公式ドキュメント](https://kubernetes.io/docs/concepts/containers/images/)と[Fairwinds のガイド](https://www.fairwinds.com/blog/kubernetes-devops-tip-5-why-setting-imagepullpolicy-to-always-is-more-necessary-than-you-think)によると:

- **latest タグ使用時は imagePullPolicy: Always が必須**
- デフォルトで latest タグは Always になるが、明示的に設定すべき
- Always でもローカルキャッシュは使われる（digest が一致すれば）

```yaml
spec:
  containers:
  - name: server
    image: server:latest
    imagePullPolicy: Always  # 必須！
```

### 2. Semantic Versioning の推奨

[Spacelift のガイド](https://spacelift.io/blog/kubernetes-imagepullpolicy)によると:

- **本番環境では semantic versioning (v1.2.3) を使うべき**
- latest は開発環境のみ
- digest による指定が最も安全

### 3. GitOps ツールの選択

[CNCF ブログ](https://www.cncf.io/blog/2023/12/01/gitops-goes-mainstream-flux-cd-boasts-largest-ecosystem/)と[比較記事](https://northflank.com/blog/flux-vs-argo-cd)によると:

```
┌──────────────────────────────────────────────────┐
│         Flux vs ArgoCD (2026)                    │
├──────────────────────────────────────────────────┤
│                                                  │
│  Flux CD:                                        │
│  ✅ Image automation built-in                   │
│  ✅ Lightweight                                  │
│  ✅ CLI-first                                    │
│  ✅ Multi-tenancy が強い                        │
│  ⚠️  UI が弱い                                  │
│                                                  │
│  ArgoCD:                                         │
│  ✅ UI が強い                                    │
│  ✅ Application-centric                         │
│  ✅ 大きなコミュニティ                          │
│  ⚠️  Image automation は外部プラグイン          │
│                                                  │
│  推奨:                                           │
│  • Solo developer → どちらでも OK               │
│  • UI 重視 → ArgoCD                             │
│  • Automation 重視 → Flux                       │
│  • ハイブリッド → 両方使う                      │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 更新された推奨

### あなたのケース（Solo dev, dev 自動, prod 手動）

#### 第1位: **Option 2 - kubectl rollout restart** ⭐⭐⭐⭐⭐

**理由:**
- 最もシンプル（10分でセットアップ）
- Commit history クリーン
- Solo developer に最適
- 追加ツール不要

**2026年のベストプラクティスとの整合性:**
- ✅ imagePullPolicy: Always 推奨と一致
- ✅ dev 環境での latest タグ使用は acceptable
- ✅ 複雑性を避ける

#### 第2位: **Option 4 - Flux CD Image Automation** ⭐⭐⭐⭐

**理由:**
- ビルトイン機能で安定
- GitOps 準拠
- ArgoCD と共存可能
- スケールしやすい

**採用タイミング:**
- 複数のマイクロサービスが増えたら
- チームが増えたら
- より厳格な GitOps が必要になったら

#### 第3位: **Option 1 - ArgoCD Image Updater** ⭐⭐⭐

**理由:**
- 既に ArgoCD を使っている場合は自然
- エコシステム内で完結

**注意点:**
- Flux より複雑（外部プラグイン）
- [2026年の記事](https://oneuptime.com/blog/post/2026-01-27-argocd-image-updater/view)でも推奨されているが、Flux のビルトイン機能には劣る

---

## 実装推奨プラン（段階的アプローチ）

### Phase 1: 今すぐ（Option 2）

```bash
# 1. backend/.github/workflows/deploy.yml に追加
# 2. imagePullPolicy: Always 設定
# 3. kubectl rollout restart で自動デプロイ
```

**所要時間:** 10分
**メリット:** 即座に動く、シンプル

### Phase 2: スケール時（Option 4 に移行）

```bash
# Flux Image Automation 導入
# 1. Flux CLI インストール
# 2. ImageRepository, ImagePolicy, ImageUpdateAutomation 作成
# 3. ArgoCD は残す（デプロイ管理）
# 4. Flux は Image Automation のみ
```

**所要時間:** 1-2時間
**メリット:** GitOps 準拠、スケーラブル、ビルトイン機能

### Phase 3: 本番環境強化（Argo Rollouts 追加）

```bash
# リスク軽減のため Canary デプロイ導入
# 1. Argo Rollouts インストール
# 2. Rollout CRD で Canary 定義
# 3. Prometheus メトリクス連携
```

**所要時間:** 半日
**メリット:** リスク最小化、自動ロールバック

---

## 結論

**今すぐのアクション:** Option 2 (kubectl rollout restart)
**将来の方向性:** Option 4 (Flux CD Image Automation)

2026年の最新ドキュメントを踏まえても、あなたのケース（Solo dev, 高頻度更新）では**シンプルさが最優先**です。

Option 2 で始めて、複雑性が必要になったら Flux に移行するのがベストプラクティスです。

---

## Sources

- [ArgoCD Image Updater Best Practices 2026](https://oneuptime.com/blog/post/2026-01-27-argocd-image-updater/view)
- [Kubernetes imagePullPolicy Guide](https://www.groundcover.com/learn/kubernetes/imagepullpolicy)
- [Flux vs ArgoCD Comparison](https://aws.plainenglish.io/argocd-vs-flux-in-2025-the-gitops-war-is-over-and-you-won-d22e084929a5)
- [Kyverno Image Mutation](https://kyverno.io/policies/other/update-image-tag/update-image-tag/)
- [Argo Rollouts Progressive Delivery](https://argoproj.github.io/rollouts/)
- [Kubernetes Images Documentation](https://kubernetes.io/docs/concepts/containers/images/)
- [CNCF GitOps Ecosystem](https://www.cncf.io/blog/2023/12/01/gitops-goes-mainstream-flux-cd-boasts-largest-ecosystem/)
