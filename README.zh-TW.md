# claude-101

> 27 個 AI 工具：MCP 伺服器 + CLI + Skill。直接跟 Claude 對話，它會搞定一切。

[![PyPI](https://img.shields.io/pypi/v/claude-101.svg)](https://pypi.org/project/claude-101/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/claude-world/claude-101/actions/workflows/ci.yml/badge.svg)](https://github.com/claude-world/claude-101/actions/workflows/ci.yml)

**[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)**

## 這是什麼？

安裝一次，獲得 24 種超能力。Claude 101 是 MCP 伺服器，給 Claude **真正的計算能力** — 統計分析、程式碼分析、SQL 解析、財務計算 — 這些都是 LLM 無法可靠完成的。

**運作原理：**

```
你：「比較 React、Vue 和 Svelte」
  ↓
Skill 指導 Claude 呼叫 build_comparison_matrix
  ↓
MCP 工具計算：Vue 8.1 > React 7.9 > Svelte 7.5（加權評分）
  ↓
Claude 回答：「Vue 以 0.2 分領先。此結果對 DX 權重敏感 —
            如果你更重視 Ecosystem，React 會勝出。」
```

**沒有 claude-101：** Claude 猜數字和排名。
**有了 claude-101：** Claude 使用精確計算，再針對結果進行推理。

## 安裝（2 分鐘）

### 步驟一：加入 MCP 伺服器

在 `.mcp.json`（專案根目錄或 `~/.claude/.mcp.json`）加入：

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

### 步驟二：安裝 Skill

Skill 教 Claude *何時*呼叫每個工具，以及*如何*使用回傳的每個欄位：

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

**完成。** 開啟新的 Claude Code session，自然對話即可。

## 24 種用法

安裝後，直接跟 Claude 說就好 — Skill 會自動處理：

### 寫作與溝通

| # | 你說... | Claude 呼叫 | 你得到 |
|---|--------|-----------|-------|
| 1 | 「幫我寫封跟進客戶的 email」 | `draft_email` | 含計算的正式度分數、Flesch 可讀性、語調分析、發送前檢查清單 |
| 2 | 「規劃一篇關於 FastAPI 的文章」 | `draft_blog_post` | 每段字數目標的大綱、SEO 欄位、關鍵詞分析、標題驗證 |
| 3 | 「整理這些會議記錄」 | `parse_meeting_notes` | 抽取與會者、行動項目（含負責人 + 截止日）、決議、討論主題 |
| 4 | 「幫這次發布寫個 Threads 貼文」 | `format_social_content` | 平台格式化文字、字數檢查、hashtag、互動信號 |
| 5 | 「幫這個專案寫 README」 | `scaffold_tech_doc` | 模板 + 程式碼結構分析、完整度評分、工時估算 |
| 6 | 「幫我規劃這本小說的結構」 | `structure_story` | 故事節拍 + 字數目標、張力曲線、節奏/對話/轉場分析 |

### 分析與研究

| # | 你說... | Claude 呼叫 | 你得到 |
|---|--------|-----------|-------|
| 7 | 「分析這份 CSV 數據」 | `analyze_data` | 逐欄統計、Pearson 相關係數、IQR 離群值偵測 |
| 8 | 「幫我摘要這份 10 頁報告」 | `summarize_document` | 關鍵句（演算法評分）、Flesch 可讀性、關鍵詞頻率 |
| 9 | 「比較這三個框架」 | `build_comparison_matrix` | 加權排名 + 分數、贏家 + 差距、敏感度分析 |
| 10 | 「分析問卷結果」 | `analyze_survey` | 逐題統計、NPS（推薦者/被動者/批評者）、滿意度 % |
| 11 | 「看看這季財報」 | `analyze_financials` | 毛利/營業/淨利率、成長率、Burn rate、Cash runway |
| 12 | 「檢查這份合約有沒有問題」 | `review_legal_document` | 18+ 條款偵測、缺失條款警示、複雜度分數、風險等級 |

### 程式與技術

| # | 你說... | Claude 呼叫 | 你得到 |
|---|--------|-----------|-------|
| 13 | 「建立一個 UserService class」 | `scaffold_code` | 依描述生成 code（CRUD/API/auth 模式）、6 語言 x 8 模式 |
| 14 | 「review 這段 code」 | `analyze_code` | 圈複雜度、巢狀深度、magic number、品質等級 A-F |
| 15 | 「解釋並優化這個 SQL」 | `process_sql` | 格式化查詢、執行計劃、效能提示（SELECT *、index 使用） |
| 16 | 「生成這些 endpoint 的 API 文件」 | `scaffold_api_doc` | OpenAPI YAML/Markdown、一致性檢查、程式碼認證偵測 |
| 17 | 「幫這個函式寫測試」 | `generate_test_cases` | 簽名解析、happy/edge/boundary 測試、覆蓋率分析 |
| 18 | 「該用 Kafka 還是 SQS？」 | `create_adr` | ADR + 技術知識庫（28 種技術）、差異化 trade-off |

### 商業與生產力

| # | 你說... | Claude 呼叫 | 你得到 |
|---|--------|-----------|-------|
| 19 | 「規劃這個 8 週專案」 | `plan_project` | WBS + 工時、里程碑、關鍵路徑、風險、資源分配 |
| 20 | 「幫我準備明天的面試」 | `prepare_interview` | 角色專屬題庫、STAR 驗證、JD 技能抽取、時間分配 |
| 21 | 「寫個投資提案」 | `scaffold_proposal` | AIDA 框架、ROI/NPV 計算、論證強度分析 |
| 22 | 「處理這個客訴」 | `build_support_response` | Issue 分類、升級風險 0-100、解決時間估算、品質評分 |
| 23 | 「寫這個功能的 PRD」 | `scaffold_prd` | User Stories、MoSCoW 排序、完整度評分、依賴偵測 |
| 24 | 「幫我做決策分析」 | `evaluate_decision` | 加權評分矩陣、排名、敏感度分析 |

## CLI 使用方式

也可以作為獨立命令列工具：

```bash
# 安裝
pip install "claude-101[mcp]"

# 列出所有工具
claude-101 list
claude-101 list --category analysis

# 直接執行任何工具
claude-101 draft-email "會議跟進" --tone assertive
claude-101 --pretty analyze-data "name,score\nAlice,95\nBob,87"
claude-101 scaffold-proposal business "雲端遷移" --investment 100000 --annual-return 50000

# 從 stdin 讀取
echo "SELECT * FROM users" | claude-101 process-sql -
cat mycode.py | claude-101 analyze-code -

# 工具說明
claude-101 draft-email --help
```

## Python 函式庫

```python
from claude_101.analysis.data import analyze_data
from claude_101.business.decision import evaluate_decision

result = analyze_data("name,score\nAlice,95\nBob,87", output_format="csv", operations="all")
result["correlations"]  # [{"column_a": "score", "column_b": "hours", "pearson_r": 0.94}]

result = evaluate_decision("A,B", "Speed,Cost", "0.6,0.4", "A:Speed=9,Cost=5;B:Speed=6,Cost=9")
result["winner"]  # {"option": "A", "score": 7.4, "margin": 0.2}
```

## 架構

```
claude-101/
  src/claude_101/
    server.py           # MCP 伺服器（27 個工具，FastMCP）
    cli.py              # CLI（從函式簽名自動生成）
    _utils.py           # 14 個共用計算函式
    _guides.py          # 24 個內建使用指南
    writing/            # 6 個工具：email、blog、meeting、social、techdoc、story
    analysis/           # 6 個工具：data、summary、comparison、survey、financial、legal
    coding/             # 6 個工具：codegen、review、sql、apidoc、testgen、adr
    business/           # 6 個工具：planning、interview、proposal、support、prd、decision
  skills/
    claude-101-mastery.md  # Skill 檔案（教 Claude 如何使用全部 24 個工具）
  tests/                   # 157 個測試，6 個測試檔
```

**依賴：** 僅 `sqlparse`（其餘皆標準函式庫）。MCP 為可選依賴。

## 貢獻

請參閱 [CONTRIBUTING.zh-TW.md](CONTRIBUTING.zh-TW.md)。版本歷史請見 [CHANGELOG.md](CHANGELOG.md)。

## 授權

MIT — 詳見 [LICENSE](LICENSE)。
