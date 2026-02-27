# 【指示書】イベント駆動バックエンド（NATS + Watermill）基本仕様書の作成要件

## 背景と目的
Liverty Musicの次世代バックエンド基盤として、Go言語とKubernetes (GKE) を活用したイベント駆動型アーキテクチャ (EDA) の基本仕様書を作成してください。
[cite_start]本構成では、リアルタイムなメッセージング基盤（ホット・データパス）に NATS JetStream を採用し [cite: 20][cite_start]、Goアプリケーション層の抽象化ライブラリとして Watermill を使用します [cite: 20][cite_start]。また、イベントログの長期保存（コールド・データパス）先として GCS (Google Cloud Storage) を活用します [cite: 20]。

## システムの前提条件・制約事項
1. **インフラストラクチャ (NATS on GKE)**
   - [cite_start]NATS JetStreamは公式Helmチャートを使用し、GKE上に3ノードのHA（高可用性）構成でデプロイすること [cite: 20]。
   - [cite_start]NATSのメッセージ永続化層には、低遅延処理のためGKEのPersistent Disk (SSD) を割り当てること [cite: 19]。
2. **アプリケーション層の設計 (Go + Watermill)**
   - [cite_start]ビジネスロジック内にNATS固有のAPIを直接記述しないこと。Watermillの `Publisher` および `Subscriber` インターフェースを用いて通信を抽象化し、インフラのベンダーロックインを排除すること [cite: 12]。
3. **長期保存アーカイバ (NATS to GCS ダンパー)**
   - [cite_start]ローカルディスクの逼迫を防ぐため、NATS JetStreamからイベントデータをサブスクライブし、バッチ処理でGCSに保存（ダンプ）する専用のGoワーカーの仕様を含めること [cite: 20]。

## 出力要求（作成すべき仕様書の目次構成）
以下の構成に従って、マークダウン形式で詳細かつ実装レベルの仕様書を出力してください。

### 1. システムアーキテクチャ概要
- 各コンポーネント（Producer API, NATS Cluster, Consumer Apps, GCS Dumper）のデータの流れを示す構成図（Mermaid記法を使用すること）。

### 2. インフラストラクチャ仕様
- GKEリソース要件と、NATS JetStreamのストレージプロビジョニング（PVC）の基本設定。
- [cite_start]NATSのマルチテナンシー（Streamの論理分割）設計の指針 [cite: 9]。

### 3. アプリケーション実装仕様 (Watermill)
- Watermill NATSアダプターの初期化設定と、環境差異（ローカルのGoChannelと本番のNATS）を吸収するDI (Dependency Injection) の方針。
- Watermill Routerを利用した標準的なミドルウェア（リトライ処理、エラーハンドリング、ログ出力）の適用方針。

### 4. GCSアーカイブ仕様（コールド・データパス）
- NATSからGCSへデータを安全に退避させるためのバッチ化ロジック（一定データサイズ、または一定時間経過によるフラッシュ処理）。
- GCSへの保存フォーマットと、オブジェクトキー（パス）の命名規則。

### 5. 運用とオートスケーリング仕様
- [cite_start]KEDAを利用したオートスケーリング設計。NATS JetStream Scalerを用いて、コンシューマーのラグ（未処理メッセージ数）に応じたPodの増減ルールを定義すること [cite: 9, 20]。
