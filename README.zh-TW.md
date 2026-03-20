# claude-101

> 27 個實用 AI 工具 — MCP 伺服器 + CLI。真實計算，零 API 費用。

[![PyPI](https://img.shields.io/pypi/v/claude-101.svg)](https://pypi.org/project/claude-101/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/claude-world/claude-101/actions/workflows/ci.yml/badge.svg)](https://github.com/claude-world/claude-101/actions/workflows/ci.yml)

**[English](README.md) | [繁體中文](README.zh-TW.md)**

## 這是什麼？

Claude 101 提供 **27 個結構化工具**，執行真正的本地計算 — 統計分析、文字解析、評分驗證、文本分析 — 回傳結構化 JSON。

**為什麼需要？** LLM 擅長生成文字，但數學運算、計數和結構化分析不可靠。這些工具負責計算，讓 LLM 專注推理。

**兩種介面：**
- **MCP 伺服器** — Claude Code 透過 MCP 協定連接
- **CLI 命令列** — 終端機直接呼叫：`claude-101 analyze-code "def foo(): pass"`

**零費用。** 不需要付費 API，所有運算都在本地 Python 完成。

## 快速開始

```bash
# 安裝
pip install "claude-101[mcp]"

# 安裝 Skill（教 Claude 如何使用全部 24 個工具）
mkdir -p ~/.claude/skills
curl -sL https://raw.githubusercontent.com/claude-world/claude-101/main/skills/claude-101-mastery.md \
  -o ~/.claude/skills/claude-101-mastery.md

# CLI — 試試看
claude-101 list
claude-101 draft-email "Q3 預算會議跟進" --tone friendly
claude-101 analyze-code "def fib(n): return n if n<2 else fib(n-1)+fib(n-2)"
claude-101 --pretty process-sql "SELECT * FROM users WHERE active = true"

# MCP 伺服器 — 給 Claude Code 使用
claude-101 serve
```

### 連接 Claude Code

在 `.mcp.json` 加入一段設定即可：

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

本地開發模式：

```json
{
  "mcpServers": {
    "claude-101": {
      "command": "python",
      "args": ["-m", "claude_101.server"],
      "cwd": "/path/to/claude-101"
    }
  }
}
```

## 全部 27 個工具

### 寫作與溝通（6 個）

| 工具 | 計算內容 |
|------|---------|
| `draft-email` | 正式度評分、Flesch 可讀性、語調分析、郵件結構驗證、發送前檢查清單 |
| `draft-blog-post` | 主題關鍵詞抽取、標題層級驗證、可讀性目標、內容缺口分析、SEO 欄位 |
| `parse-meeting-notes` | 正則抽取：與會者、行動項目（負責人 + 截止日）、決議、討論主題、時間戳 |
| `format-social-content` | 平台感知分段、Hashtag 抽取、互動信號偵測（提問/CTA/hook 強度） |
| `scaffold-tech-doc` | 8 種文件模板 + 工時估算；可選：程式碼結構解析、README 完整度評分 |
| `structure-story` | 張力曲線插值、字數目標；可選：節奏分析、對話比例、場景轉場偵測 |

### 分析與研究（6 個）

| 工具 | 計算內容 |
|------|---------|
| `analyze-data` | 逐欄統計（mean/median/stdev）、Pearson 相關係數、IQR 離群值偵測 |
| `summarize-document` | 萃取式摘要（句子評分）、Flesch 可讀性、關鍵詞頻率 |
| `build-comparison-matrix` | 權重正規化、關鍵權重識別、敏感度分析框架 |
| `analyze-survey` | 逐題分佈、NPS 計算（推薦者/被動者/批評者）、滿意度分數 |
| `analyze-financials` | 毛利率/營業利率/淨利率、期間成長率、Burn rate、Cash runway |
| `review-legal-document` | 18+ 條款模式比對、風險等級、缺失條款警示、複雜度分數 |

### 程式與技術（6 個）

| 工具 | 計算內容 |
|------|---------|
| `scaffold-code` | 6 種語言 x 8 種設計模式的程式碼模板 |
| `analyze-code` | 語言偵測、圈複雜度、巢狀深度、問題偵測、品質等級 A-F |
| `process-sql` | SQL 解析/格式化（sqlparse）、方言偵測、結構抽取 |
| `scaffold-api-doc` | 端點解析、OpenAPI/Markdown 生成、API 一致性檢查、認證模式偵測 |
| `generate-test-cases` | 函式簽名解析、happy/edge/boundary 測試生成、覆蓋率分析 |
| `create-adr` | 架構決策紀錄 + 權衡矩陣 |

### 商業與生產力（6 個）

| 工具 | 計算內容 |
|------|---------|
| `plan-project` | WBS 分解、里程碑、關鍵路徑、風險識別、工時估算 |
| `prepare-interview` | 角色/級別題庫策展、難度平衡、時間分配；可選：JD 技能抽取、STAR 回答驗證 |
| `scaffold-proposal` | AIDA 覆蓋評分；可選：論證強度分析（主張 vs 證據）、ROI/NPV 計算 |
| `build-support-response` | Issue 分類、升級風險 0-100、解決時間估算、客戶投入度；可選：回應品質評分 |
| `scaffold-prd` | MoSCoW 自動排序、需求完整度評分、User Story 品質驗證、功能依賴偵測 |
| `evaluate-decision` | 加權評分、排名、敏感度分析（+-10% 權重模擬） |

### Meta（3 個）

| 工具 | 功能 |
|------|------|
| `list-guides` | 瀏覽 24 個使用案例指南 |
| `get-guide` | 取得完整指南（含提示和步驟） |
| `search-guides` | 全文搜尋指南 |

## CLI 使用方式

```bash
# 列出所有工具
claude-101 list
claude-101 list --category analysis

# 執行工具（位置參數 + 可選旗標）
claude-101 draft-email "會議跟進" --tone assertive --format brief
claude-101 scaffold-prd "TaskFlow" "團隊需要更好的任務追蹤" --target-users "PM, Engineer"
claude-101 scaffold-proposal business "雲端遷移" --investment 100000 --annual-return 50000

# 美化 JSON 輸出
claude-101 --pretty analyze-data "name,score\nAlice,95\nBob,87" --format csv

# 從 stdin 讀取
echo "SELECT * FROM users" | claude-101 process-sql -
cat mycode.py | claude-101 analyze-code -

# 工具說明
claude-101 draft-email --help
```

## Python 函式庫

```python
from claude_101.writing.email import draft_email
from claude_101.analysis.data import analyze_data
from claude_101.coding.review import analyze_code
from claude_101.business.decision import evaluate_decision

# 所有函式回傳 dict
result = draft_email("投資提案", tone="professional")
result["text_analysis"]["formality_score"]  # 73.5
result["text_analysis"]["readability"]["flesch_grade"]  # "Standard (8th-9th grade)"
```

## 開發

```bash
git clone https://github.com/claude-world/claude-101.git
cd claude-101
pip install -e ".[all]"
pip install pytest ruff

# 跑測試（160 個）
pytest

# Lint 檢查
ruff check src/

# 本地啟動 MCP 伺服器
python -m claude_101.server
```

## 架構

```
src/claude_101/
    __init__.py         # 套件版本
    _utils.py           # 14 個共用工具（統計、文本分析、評分）
    _guides.py          # 24 個內建使用指南
    server.py           # MCP 伺服器（FastMCP 包裝層）
    cli.py              # CLI 介面（argparse，從函式簽名自動生成）
    writing/            # 6 個寫作工具
    analysis/           # 6 個分析工具
    coding/             # 6 個程式工具
    business/           # 6 個商業工具
tests/
    test_writing.py     # 48 個測試
    test_business.py    # 40 個測試
    test_coding.py      # 25 個測試
    test_analysis.py    # 11 個測試
    test_cli.py         # 24 個測試
    test_server.py      # 12 個測試
```

**依賴：** 僅 `sqlparse`（其餘皆用標準函式庫）。MCP 為可選依賴。

## Skill 系統

`skills/claude-101-mastery.md` 教 Claude 如何完美執行所有 24 種用法。安裝一次即可：

```bash
mkdir -p ~/.claude/skills
cp skills/claude-101-mastery.md ~/.claude/skills/
```

**Skill 做什麼：**
- 將用戶意圖對應到正確的 MCP 工具
- 告訴 Claude 要使用哪些回傳欄位、怎麼用
- 確保 Claude 產出以真實計算為基礎的高品質結果
- 沒有 Skill：Claude 會用工具。有了 Skill：Claude **精通**工具。

## 貢獻

請參閱 [CONTRIBUTING.zh-TW.md](CONTRIBUTING.zh-TW.md)。版本歷史請見 [CHANGELOG.md](CHANGELOG.md)。

## 授權

MIT — 詳見 [LICENSE](LICENSE)。
