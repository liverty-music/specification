# Ticket System MVP - Use Case Guide

This document explains the ticket system's use cases in plain language,
intended for non-technical stakeholders.

---

## Actors

| Actor | Description |
|-------|-------------|
| **Fan** | A music fan who wants to attend a live event. Obtains and uses tickets via their smartphone browser. |
| **Venue Staff** | Staff at the event venue entrance who verify that a fan's ticket is authentic. |
| **System** | Automated server-side processing (not a human). |

---

## Glossary

| Term | Meaning |
|------|---------|
| **Soulbound Token (SBT)** | A digital ticket that, once issued, **cannot be transferred or resold** to another person. Think of it as a paper ticket with your name written in permanent ink. |
| **Mint** | To newly "issue" a digital ticket. The word comes from the same origin as a mint (facility) that produces coins. |
| **Blockchain** | A tamper-proof public ledger. Ticket issuance records are stored here, making forgery impossible. |
| **Merkle Tree** | A tree-shaped data structure that aggregates all ticket holders' data. Using this structure, you can mathematically prove "I am one of the ticket holders" **without revealing the full list of holders**. |
| **Merkle Path** | The data representing the route from "your position" to the "top (root)" within the Merkle Tree. With this path, you can prove that you are included in the tree. |
| **Zero-Knowledge Proof (ZKP)** | A cryptographic technique that proves the fact "I hold a ticket" **without revealing who you are (no personal information disclosed)**. Think of it as proving "I am a Japanese citizen" without showing your passport. |
| **QR Code** | A two-dimensional barcode displayed on your smartphone screen. It contains the zero-knowledge proof data inside. |
| **Nullifier** | A "used stamp." Like a stamp pressed on a ticket that has already been used for entry, it prevents the same QR code from being used to enter twice. |

---

## Use Cases

### UC1: Issue a Ticket (Mint Soulbound Ticket)

- **Actor**: Fan (login required)
- **What happens**: The fan selects an event and taps "Get Ticket." A **non-transferable digital ticket (SBT)** is then issued on the blockchain.
- **Key point**: The same fan cannot obtain duplicate tickets for the same event. No matter how many times the button is pressed, only one ticket is issued.

### UC2: View Ticket Details (Get Ticket Details)

- **Actor**: Anyone (no login required)
- **What happens**: By specifying a ticket ID, anyone can view information about that ticket (which event it is for, when it was issued, etc.).

### UC3: View My Tickets (List My Tickets)

- **Actor**: Fan (login required)
- **What happens**: Displays a list of all tickets the fan owns. For security, other users' tickets are not visible.

### UC4: Retrieve Entry Preparation Data (Get Merkle Path)

- **Actor**: Fan (login required)
- **What happens**: The fan retrieves the **Merkle Path** (positional data within the tree) from the server. This is the material-gathering step needed to create a QR code in the next step (UC5).

### UC5: Generate Entry QR Code (Generate Entry Code)

- **Actor**: Fan (no login required; completes entirely on the smartphone)
- **What happens**: Using the data obtained in UC4, the smartphone browser **locally** computes a zero-knowledge proof and displays it as a QR code on the screen.
- **Key point**: Once the data is downloaded, it works even offline (out of cellular range). It proves the fact "I hold a ticket" **without revealing who the ticket holder is**.

### UC6: Verify Entry at Venue (Verify Entry at Venue)

- **Actor**: Venue Staff
- **What happens**: Staff scans the QR code displayed on the fan's smartphone and the server verifies the zero-knowledge proof. If valid, entry is permitted and a **nullifier (used stamp)** is recorded.
- **Key point**: Attempting to enter twice with the same QR code is automatically blocked.

### UC7: Build Merkle Tree (Build Merkle Tree)

- **Actor**: System (automated processing)
- **What happens**: After ticket sales close, the system builds a **Merkle Tree** from all ticket holders' data. This becomes the foundation for entry verification in UC4 through UC6.

---

## End-to-End Flow (Fan Experience)

```
1. Ticket Purchase  ->  2. System Prep  ->  3. QR Code Generation  ->  4. Venue Entry
      (UC1)                 (UC7)              (UC4 -> UC5)                (UC6)

  Fan selects an        After ticket         On the day of the        Staff scans QR
  event in the app      sales close,         event, the fan           code at the
  and obtains a         the system           generates a QR code      venue entrance
  ticket                automatically        on their smartphone      -> entry allowed
                        builds the tree      (works offline)
```

---

## アクター（誰が操作するのか）

| アクター | 説明 |
|----------|------|
| **ファン（Fan）** | ライブに行きたい音楽ファン。スマホのブラウザからチケットを取得・利用する |
| **会場スタッフ（Venue Staff）** | ライブ会場の入口で、ファンのチケットが本物かを確認する係員 |
| **システム（System）** | 人間ではなく、サーバーが自動的に行う内部処理 |

---

## 用語解説

| 用語 | 意味 |
|------|------|
| **Soulbound Token（SBT）** | 「魂に紐づくトークン」の意味。一度発行されたら**他人に譲渡・転売できない**デジタルチケットのこと。紙チケットに自分の名前が消せないインクで書かれているイメージ |
| **Mint（ミント）** | デジタルチケットを新しく「発行する」こと。造幣局（mint）が硬貨を鋳造するのと同じ語源 |
| **ブロックチェーン** | 改ざんできない公開台帳。チケットの発行記録がここに残るため、偽造が不可能になる |
| **Merkle Tree（マークルツリー）** | チケット保有者全員のデータをツリー（木）構造にまとめたもの。これを使うと「自分がチケット保有者の一人である」ことを、**全員分のリストを見せなくても**数学的に証明できる |
| **Merkle Path（マークルパス）** | マークルツリーの中で「自分の位置」から「頂上（ルート）」までの道筋のデータ。この道筋があれば、自分がツリーに含まれていることを証明できる |
| **ゼロ知識証明（ZKP）** | 「自分がチケットを持っている」という事実だけを証明し、**誰であるか（個人情報）は一切明かさない**暗号技術。例えるなら、パスポートを見せずに「日本国籍です」とだけ証明できるようなもの |
| **QRコード** | スマホの画面に表示される二次元バーコード。この中にゼロ知識証明のデータが入っている |
| **Nullifier（ナリファイア）** | 「使用済み印」のこと。一度入場に使ったQRコードに押されるスタンプのようなもので、同じQRコードで2回入場することを防ぐ |

---

## ユースケース

### UC1: チケットを発行する（Mint Soulbound Ticket）

- **アクター**: ファン（ログイン必須）
- **やること**: ファンがイベントを選んで「チケットを取得」ボタンを押すと、ブロックチェーン上に**転売できないデジタルチケット（SBT）**が発行される
- **ポイント**: 同じファンが同じイベントのチケットを二重に取得することはできない（何度ボタンを押しても1枚だけ発行される）

### UC2: チケットの詳細を見る（Get Ticket Details）

- **アクター**: 誰でも（ログイン不要）
- **やること**: チケットIDを指定して、そのチケットの情報（どのイベントか、いつ発行されたか等）を確認する

### UC3: 自分のチケット一覧を見る（List My Tickets）

- **アクター**: ファン（ログイン必須）
- **やること**: 自分が持っているチケットの一覧を表示する。セキュリティ上、他人のチケットは見えない

### UC4: 入場準備データを取得する（Get Merkle Path）

- **アクター**: ファン（ログイン必須）
- **やること**: サーバーから**マークルパス**（ツリー内での自分の位置データ）を取得する。次のステップ（UC5）でQRコードを作るために必要な材料集め

### UC5: 入場用QRコードを生成する（Generate Entry Code）

- **アクター**: ファン（ログイン不要、スマホだけで完結）
- **やること**: UC4で取得したデータを使い、**スマホのブラウザ内だけで**ゼロ知識証明を計算し、QRコードとして画面に表示する
- **ポイント**: 一度データをダウンロードすればオフライン（圏外）でも動作する。**「誰がチケットを持っているか」を明かさずに、「持っている」という事実だけを証明できる**

### UC6: 会場で入場を確認する（Verify Entry at Venue）

- **アクター**: 会場スタッフ
- **やること**: ファンのスマホに表示されたQRコードをスキャンし、サーバーでゼロ知識証明を検証する。正しければ入場を許可し、**ナリファイア（使用済み印）**を記録する
- **ポイント**: 同じQRコードを使って2回入場しようとすると自動的にブロックされる

### UC7: Merkle Tree を構築する（Build Merkle Tree）

- **アクター**: システム（自動処理）
- **やること**: チケット販売終了後、全チケット保有者のデータから**マークルツリー**を構築する。これがUC4〜UC6の入場検証の土台になる

---

## 全体の流れ（ファンの体験）

```
① チケット購入  ──→  ② システム準備  ──→  ③ QRコード生成  ──→  ④ 会場入場
   (UC1)                (UC7)              (UC4 → UC5)          (UC6)

 ファンがアプリで     チケット販売終了後    ライブ当日、        会場入口で
 イベントを選び      システムが自動で      スマホでQRコードを   スタッフがスキャン
 チケットを取得      ツリーを構築          生成（オフラインOK）  → 入場許可
```
