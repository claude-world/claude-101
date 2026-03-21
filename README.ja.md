# claude-101

> 27個のAIツール：MCPサーバー + CLI + Skill。Claudeに話しかけるだけ。

[![PyPI](https://img.shields.io/pypi/v/claude-101.svg)](https://pypi.org/project/claude-101/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/claude-world/claude-101/actions/workflows/ci.yml/badge.svg)](https://github.com/claude-world/claude-101/actions/workflows/ci.yml)

**[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)**

## これは何？

一度インストールすれば24のスーパーパワーを獲得。Claude 101はMCPサーバーで、Claudeに**実際の計算能力**を与えます — 統計分析、コード分析、SQL解析、財務計算など、LLM単体では信頼性の低い処理を担当します。

**仕組み：**

```
あなた：「React、Vue、Svelteを比較して」
  ↓
SkillがClaudeにbuild_comparison_matrixの呼び出しを指示
  ↓
MCPツールが計算：Vue 8.1 > React 7.9 > Svelte 7.5（加重スコアリング）
  ↓
Claudeの回答：「Vueが0.2ポイント差でリード。この結果はDXの重みに
              敏感です。Ecosystemをより重視するとReactが逆転します。」
```

**claude-101なし：** Claudeは数値やランキングを推測。
**claude-101あり：** Claudeは正確な計算結果を使い、その上で推論。

## セットアップ（2分）

### ステップ1：MCPサーバーを追加

`.mcp.json`（プロジェクトルートまたは `~/.claude/.mcp.json`）に追加：

```json
{
  "mcpServers": {
    "claude-101": {
      "command": "uvx",
      "args": ["--from", "claude-101[mcp]", "claude-101-server"]
    }
  }
}
```

### ステップ2：Skillをインストール

Skillは、Claudeに各ツールを*いつ*呼び出すか、結果の各フィールドを*どう*使うかを教えます：

```bash
mkdir -p ~/.claude/skills/claude-101-mastery/references
cd ~/.claude/skills/claude-101-mastery
BASE=https://raw.githubusercontent.com/claude-world/claude-101/main/skills/claude-101-mastery
curl -sLO $BASE/SKILL.md
curl -sLO $BASE/references/writing-workflows.md   --output-dir references
curl -sLO $BASE/references/analysis-workflows.md   --output-dir references
curl -sLO $BASE/references/coding-workflows.md     --output-dir references
curl -sLO $BASE/references/business-workflows.md   --output-dir references
```

**完了。** 新しいClaude Codeセッションを開始して、自然に話しかけてください。

## 24のユースケース

セットアップ後、Claudeに頼むだけ — Skillが自動で処理します：

### ライティング＆コミュニケーション

| # | あなたが言うこと | Claudeが呼び出す | 得られるもの |
|---|---------------|----------------|------------|
| 1 | 「クライアントへのフォローアップメールを書いて」 | `draft_email` | フォーマリティスコア、Flesch読みやすさ、トーン分析、送信前チェックリスト |
| 2 | 「FastAPIについてブログ記事を企画して」 | `draft_blog_post` | セクション別の目標語数、SEOフィールド、キーワード分析、見出し検証 |
| 3 | 「この会議メモを整理して」 | `parse_meeting_notes` | 参加者、アクションアイテム（担当者+期限）、決定事項、トピック |
| 4 | 「このローンチ用のThreads投稿を作って」 | `format_social_content` | プラットフォーム対応テキスト、文字数チェック、ハッシュタグ、エンゲージメント信号 |
| 5 | 「このプロジェクトのREADMEを書いて」 | `scaffold_tech_doc` | テンプレート+コード構造分析、完全性スコア、工数見積もり |
| 6 | 「この小説の構成を手伝って」 | `structure_story` | ストーリービート+目標語数、テンション曲線、ペーシング/会話/場面転換分析 |

### 分析＆リサーチ

| # | あなたが言うこと | Claudeが呼び出す | 得られるもの |
|---|---------------|----------------|------------|
| 7 | 「このCSVデータを分析して」 | `analyze_data` | 列ごとの統計量、ピアソン相関係数、IQR外れ値検出 |
| 8 | 「この10ページのレポートを要約して」 | `summarize_document` | キーセンテンス（アルゴリズム評価）、Flesch読みやすさ、キーワード頻度 |
| 9 | 「この3つのフレームワークを比較して」 | `build_comparison_matrix` | 加重ランキング+スコア、勝者+マージン、感度分析 |
| 10 | 「アンケート結果を分析して」 | `analyze_survey` | 質問別統計、NPSスコア（推奨者/中立者/批判者）、満足度% |
| 11 | 「今四半期の財務を確認して」 | `analyze_financials` | 粗利/営業/純利益率、成長率、バーンレート、キャッシュランウェイ |
| 12 | 「この契約書に問題がないかチェックして」 | `review_legal_document` | 18+条項検出、欠落条項アラート、複雑度スコア、リスクレベル |

### コーディング＆テクニカル

| # | あなたが言うこと | Claudeが呼び出す | 得られるもの |
|---|---------------|----------------|------------|
| 13 | 「UserServiceクラスを作って」 | `scaffold_code` | 説明に応じたコード（CRUD/API/authパターン）、6言語×8パターン |
| 14 | 「このコードをレビューして」 | `analyze_code` | 循環的複雑度、ネスト深度、マジックナンバー、品質グレードA-F |
| 15 | 「このSQLを説明して最適化して」 | `process_sql` | フォーマット、実行計画、パフォーマンスヒント（SELECT*、インデックス利用） |
| 16 | 「このエンドポイントのAPIドキュメントを生成して」 | `scaffold_api_doc` | OpenAPI YAML/Markdown、一貫性チェック、認証パターン検出 |
| 17 | 「この関数のテストを書いて」 | `generate_test_cases` | シグネチャ解析、happy/edge/boundaryケース、カバレッジ分析 |
| 18 | 「KafkaとSQS、どちらを使うべき？」 | `create_adr` | ADR+技術ナレッジベース（28技術）、差別化されたトレードオフ |

### ビジネス＆プロダクティビティ

| # | あなたが言うこと | Claudeが呼び出す | 得られるもの |
|---|---------------|----------------|------------|
| 19 | 「この8週間プロジェクトを計画して」 | `plan_project` | WBS+工数、マイルストーン、クリティカルパス、リスク、リソース配分 |
| 20 | 「明日の面接の準備を手伝って」 | `prepare_interview` | ロール別質問集、STAR検証、JDスキル抽出、時間配分 |
| 21 | 「ビジネス提案書を書いて」 | `scaffold_proposal` | AIDAフレームワーク、ROI/NPV計算、論拠強度分析 |
| 22 | 「この怒っている顧客に対応して」 | `build_support_response` | 問題分類、エスカレーションリスク0-100、解決時間見積もり、品質スコア |
| 23 | 「この機能のPRDを作成して」 | `scaffold_prd` | ユーザーストーリー、MoSCoW優先度付け、完全性スコア、依存関係検出 |
| 24 | 「これらの選択肢の意思決定分析をして」 | `evaluate_decision` | 加重スコアリングマトリクス、ランキング、感度分析 |

## CLI使用方法

スタンドアロンのコマンドラインツールとしても使用可能：

```bash
# インストール
pip install "claude-101[mcp]"

# 全ツール一覧
claude-101 list
claude-101 list --category analysis

# 任意のツールを直接実行
claude-101 draft-email "meeting follow-up" --tone assertive
claude-101 --pretty analyze-data "name,score\nAlice,95\nBob,87"
claude-101 scaffold-proposal business "Cloud Migration" --investment 100000 --annual-return 50000

# stdinからパイプ
echo "SELECT * FROM users" | claude-101 process-sql -
cat mycode.py | claude-101 analyze-code -

# ツールヘルプ
claude-101 draft-email --help
```

## Pythonライブラリ

```python
from claude_101.analysis.data import analyze_data
from claude_101.business.decision import evaluate_decision

result = analyze_data("name,score\nAlice,95\nBob,87", output_format="csv", operations="all")
result["correlations"]  # [{"column_a": "score", "column_b": "hours", "pearson_r": 0.94}]

result = evaluate_decision("A,B", "Speed,Cost", "0.6,0.4", "A:Speed=9,Cost=5;B:Speed=6,Cost=9")
result["winner"]  # {"option": "A", "score": 7.4, "margin": 0.2}
```

## アーキテクチャ

```
claude-101/
  src/claude_101/
    server.py           # MCPサーバー（27ツール、FastMCP）
    cli.py              # CLI（関数シグネチャから自動生成）
    _utils.py           # 14の共有計算関数
    _guides.py          # 24の組み込みユースケースガイド
    writing/            # 6ツール：email、blog、meeting、social、techdoc、story
    analysis/           # 6ツール：data、summary、comparison、survey、financial、legal
    coding/             # 6ツール：codegen、review、sql、apidoc、testgen、adr
    business/           # 6ツール：planning、interview、proposal、support、prd、decision
  skills/
    claude-101-mastery.md  # Skillファイル（24ツール全ての使い方をClaudeに教える）
  tests/                   # 157テスト、6テストファイル
```

**依存関係：** `sqlparse`のみ（それ以外は標準ライブラリ）。MCPはオプション。

## コントリビュート

[CONTRIBUTING.md](CONTRIBUTING.md)をご参照ください。リリース履歴は[CHANGELOG.md](CHANGELOG.md)をご覧ください。

## ライセンス

MIT — [LICENSE](LICENSE)を参照。
