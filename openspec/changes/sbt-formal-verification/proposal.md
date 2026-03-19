## Why

Phase 1 (sbt-test-hardening) でテストの穴を塞ぎ Slither を導入した後、mainnet デプロイ前に更に高い保証レベルが必要。Fuzz テストは「ランダムなサンプル」でしかなく、「全ての入力で安全」を証明できない。Halmos による形式検証で SBT の不変条件を数学的に証明し、Invariant テストで状態遷移全体を網羅し、Mutation テストでテストスイート自体の品質を客観的に測定する。

## What Changes

- Halmos によるシンボリック実行テストを追加し、SBT の全不変条件を全入力空間で証明
- Foundry invariant テスト（Handler パターン）を追加し、ランダムなトランザクションシーケンスに対する不変条件を検証
- Aderyn 静的解析を CI に追加し、Slither と併用してセカンドオピニオンを提供
- vertigo-rs による mutation テストを実行し、テストスイートの品質を定量化
- `forge coverage` による lcov レポートを CI に追加

## Capabilities

### New Capabilities

- `sbt-formal-verification`: Halmos シンボリック実行による SBT 不変条件の網羅的証明と Foundry invariant テスト
- `sbt-quality-assurance`: Aderyn 静的解析、mutation テスト（vertigo-rs）、カバレッジレポートによるテスト品質の定量化と CI 統合

### Modified Capabilities

(none)

## Impact

- `backend/contracts/test/`: Halmos 用テストファイル、invariant テスト用 Handler コントラクトの新規追加
- `.github/workflows/test.yml`: Halmos ジョブ、Aderyn ジョブ、coverage ジョブの追加
- `backend/contracts/foundry.toml`: invariant テスト設定の追加
- 開発依存: `halmos` (pip), `aderyn` (cargo/npm), `vertigo-rs` (cargo)
