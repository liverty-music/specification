Spotifyの商用利用制限（開発モードの延長制限やクォータ問題）は個人開発者にとって大きな壁ですので、**YouTube Data APIへのピボットは非常に現実的で賢明な判断**です。

特に日本ではYouTubeで音楽を聴く層が圧倒的に多いため、ターゲットユーザー層とも合致します。ただし、Spotifyと異なり「音楽以外の動画（猫の動画やYouTuberの動画）」がノイズとして混ざるため、**「アーティストの推測（Inference）」プロセスにGemini（LLM）の力を借りる**設計に変更します。

以下に、修正した仕様書を出力します。

---

# Liverty Music MVP: Onboarding & Dashboard Specification (Rev. 2)

**Version:** 2.0 (YouTube Pivot Edition)
**Target Phase:** MVP
**Core Concept:** "Pain Killer" - 最短距離でユーザーの「見逃し（FOMO）」を解消する。

## 1. 概要 (Overview)

本仕様書は、ユーザーがLPに着地してから、初期データ構築（Loading）を経て、最初のライブ情報（Dashboard）を目にするまでのUXフローおよび技術要件を定義する。
**変更点:** データソースをSpotifyから**YouTube**に変更。ユーザーの視聴行動から好みのアーティストを推測し、ライブ情報を提案する。

## 2. ユーザーストーリー (User Flow)

1. **Landing:** ユーザーはLPにアクセスする。
2. **Auth (Google Only):** Googleアカウントでサインインし、同時にYouTubeデータの読み取り権限を許可する。
3. **The Wait (Magic Moment):** YouTubeの膨大な履歴から「音楽」だけをAIが抽出・解析し、ライブ情報を探す様子が可視化される（約10〜15秒）。
4. **Discovery:** 待機後、YouTubeでよく聴くアーティストのライブ情報が並んだダッシュボードが表示される。

## 3. 機能要件 (Functional Requirements)

### 3.1 認証 (Authentication)

* **Provider:** **Google Sign-in (必須)** & Passkey (Optional).
* *Note:* Apple Music / Spotify連携はスコープ外とする。


* **Scopes:**
* `profile`, `email` (基本情報)
* `https://www.googleapis.com/auth/youtube.readonly` (YouTubeデータの参照)


* **Backend:** Go / GCP / **Zitadel (Self-hosted IdP)**.
* *Note:* Auth0 / Firebase は使用しない。認証基盤は全て Zitadel で統一する。

### 3.2 データインポート & アーティスト推測 (Data Import & Inference)

* **Trigger:** Googleサインイン完了と同時にバックグラウンドで開始。
* **YouTube Data API Logic:**
以下の2つのソースからデータを取得する（コストの低い `list` 系メソッドを使用）。
1. **Subscriptions:** `subscriptions.list` (mine=true)
* ユーザーが登録しているチャンネル名を取得。


2. **Liked Videos:** `videos.list` (myRating=like)
* 直近の高評価動画の「タイトル」と「チャンネル名」を取得（上限50件程度）。




* **Artist Filtering (By Gemini):**
* YouTubeデータには音楽以外（Vlog, ゲーム実況など）が含まれるため、**Gemini Flash** 等の高速モデルにリストを渡し、アーティスト名のみを抽出させる。
* *Prompt例:* 「以下のリストから、音楽アーティストまたはバンドの名前だけを抽出してJSON配列で返して。YouTuberやゲーム実況者は除外して。」



### 3.3 ライブ情報構築ロジック (The Brain)

* **Step A (DB Check):**
* 抽出されたアーティストがDBにあり、未来のライブ情報がある  即時採用。


* **Step B (AI Search via Gemini API):**
* **条件:** DBに情報がない、または情報の鮮度が古いアーティスト。
* **Action:** Gemini API (Grounding with Google Search) をコールし、ツアー情報を抽出。
* **Timeout:** **10秒 (Hard Limit)**。



## 4. UI/UX仕様：Loading演出 (The "Benevolent Deception")

YouTubeデータの「ノイズ除去」プロセスが入るため、演出のストーリーを微修正する。

**総所要時間:** 最大10〜15秒

| Step | 秒数目安 | 表示テキスト (Main Message) | サブテキスト / 演出 | 裏側の処理 |
| --- | --- | --- | --- | --- |
| **1** | 0s - 3s | **YouTubeの活動履歴を取得中...** | `登録チャンネルと高評価動画を読み込んでいます` | YouTube Data API Call |
| **2** | 3s - 6s | **あなたの推しアーティストを推測中...** | `AIが動画リストから音楽アーティストを抽出しています` | **Gemini (Filtering)**<br>

<br>音楽以外の動画を除外 |
| **3** | 6s - 12s | **🤖 ツアー・ライブ情報を検索中...** | `公式SNSや会場サイトを巡回しています...`<br>

<br>`(※約5秒かかります)` | **Gemini (Search)**<br>

<br>公式サイト情報の検索 |
| **4** | 12s - | **✨ あなた専用の画面を構築しました** | `All Checks Passed ✅`<br>

<br>`Redirecting...` | Dashboard描画準備 |

* **Design Note:**
* Step 2で「雑多な動画アイコン」から「マイクやギターのアイコン」が選別されていくようなアニメーションを入れると、AIの仕事を直感的に伝えられる。



## 5. ダッシュボード表示仕様 (Dashboard View)

1. **Priority 1: Confirmed Tickets (確定情報)**
* 推測されたアーティストのチケット販売中公演。


2. **Priority 2: AI Suggestions**
* 「YouTubeでよく聴いている〇〇のライブが見つかりました」というコンテキストを表示。


3. **Fallback:**
* 情報が取れなかった場合、「人気急上昇のライブ」を表示。



## 6. 技術的制約 (Constraints)

* **YouTube API Quota:**
* `search` エンドポイント（コスト100）は使用せず、必ず `list` 系（コスト1）を使用すること。


* **Data Accuracy:**
* YouTubeのチャンネル名は「Official」がついたり表記揺れが激しいため、Geminiによる名寄せ（Normalization）を挟むことが必須。



---

### 開発者への申し送り事項 (Dev Note)

* **実装の肝:** YouTubeデータはSpotifyと違って「非構造化データ」に近い状態です。そのままDB検索にかけるとヒット率が下がります。**「YouTube APIの結果を一度Geminiに投げて、クリーンなアーティスト名リストに変換してからDB検索/Web検索にかける」**というパイプラインを厳守してください。
