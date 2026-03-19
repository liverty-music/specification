## Context

TicketSBT は ERC-721 + ERC-5192 Soulbound Token で、OpenZeppelin の ERC721 と AccessControl を継承している。Base Sepolia にデプロイ済み（`0x7C50bdF2E5d6B81F71868d5B6B59B5B3EC2F06fa`）。現在のテストは 7 件で基本機能をカバーするが、SBT としての完全性（approve ブロック、全 transfer パスの遮断）やエッジケース、ロール管理のテストが不足している。CI は `forge test -vvv` のみで、静的解析やガス監視は未導入。

## Goals / Non-Goals

**Goals:**
- テストカバレッジの穴を特定・網羅し、全ての SBT 不変条件をテストで保証する
- approve / setApprovalForAll を override して revert させ、SBT の意味論的完全性を担保する
- Slither 静的解析を CI に組み込み、既知脆弱性パターンを自動検出する
- forge snapshot でガスベースラインを確立し、回帰を検知する
- Foundry fuzz テストで、ランダム入力に対する堅牢性を検証する

**Non-Goals:**
- Invariant テスト（Handler パターン設計が必要 → Phase 2）
- Halmos による形式検証（→ Phase 2）
- Mutation テスト（テストスイート完成後に実施 → Phase 2）
- Aderyn の導入（Slither で Phase 1 は十分 → Phase 2）
- mainnet デプロイ

## Decisions

### D1: approve / setApprovalForAll を override して revert させる

**選択:** コントラクト側で `approve` と `setApprovalForAll` を override し、無条件に revert させる。

**理由:** SBT は転送不可であるため、approve が成功すること自体が意味論的に矛盾する。transferFrom が revert するため実害はないが、ユーザーがガスを無駄に消費し、外部ツール（マーケットプレイス等）が approve 成功を「転送可能」と誤解するリスクがある。

**代替案:** テストだけで「approve しても transfer できない」ことを検証する → 不採用。根本原因（approve が通ること）を解消すべき。

### D2: Slither を CI に追加する方法

**選択:** `crytic/slither-action` GitHub Action を `test.yml` の contracts パスフィルタ配下に新規ジョブとして追加。forge-test ジョブと並列実行。

**理由:** 公式 Action があり、Foundry プロジェクトを自動認識する。セットアップコストが最小。

**代替案:** ローカル実行のみ → 不採用。CI で自動実行しないと漏れが発生する。

### D3: fuzz-runs の設定値

**選択:** CI では `--fuzz-runs 10000`、foundry.toml のデフォルトは `256`（ローカル開発用）のまま。

**理由:** コミュニティ推奨は CI で 10000 以上。ローカルは速度重視で 256 のまま。CI 側でのみ override する。

### D4: テスト構造

**選択:** 既存の `TicketSBT.t.sol` にテストを追加する（新規ファイルは作らない）。

**理由:** コントラクトが 1 つで小さいため、テストを分割するメリットがない。セクションコメントで整理する。

## Risks / Trade-offs

- **[Risk] approve override が既存デプロイに影響** → Mitigation: Base Sepolia のコントラクトは immutable。新しいコントラクトとして再デプロイが必要。Phase 1 ではコード変更のみ行い、再デプロイは別途判断。
- **[Risk] Slither の false positive** → Mitigation: `.slither.config.json` でプロジェクト固有の除外ルールを設定。初回実行時に結果をトリアージし、false positive は明示的に除外。
- **[Risk] fuzz-runs 10000 で CI が遅くなる** → Mitigation: 現在のコントラクトは小さいため 10000 runs でも数秒で完了する見込み。CI timeout 10 分以内に収まることを確認。
