# note-reviewer

ブログ記事・技術メモの Markdown をレビューする Claude Code プラグイン。

## できること

`/review <ファイルパス>` で対象の Markdown を以下の観点でレビューする。

- **校閲** — 誤字脱字・文法・表記ゆれ・冗長表現を、筆者の文体を保ったまま修正
- **個人情報チェック** — 実名・連絡先・認証情報・社内情報などを検出して警告
- **タイトル案** — 最大10個
- **ハッシュタグ案** — Qiita / Zenn / X を想定
- **骨格モード** — 見出しや箇条書きだけの状態を肉付けして本文化

**元ファイルは編集しません。** 校閲結果は同じディレクトリの `_review/` 配下に新規ファイルとして出力します（`<元ファイル名>-校閲.md`、必要なら `-構成案.md`）。タイトル・ハッシュタグ・個人情報チェックはチャットに出力します。

## インストール

```
/plugin marketplace add <あなたのGitHubユーザー名>/note-reviewer-plugin
/plugin install note-reviewer@note-reviewer-marketplace
```

## 開発時（ローカル確認）

```
/plugin marketplace add /path/to/note-reviewer-plugin
/plugin install note-reviewer@note-reviewer-marketplace
```

修正後は `/plugin marketplace update note-reviewer-marketplace` で再読み込み。

## 使い方

```
/review path/to/記事.md
```
