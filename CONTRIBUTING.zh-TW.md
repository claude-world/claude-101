# 貢獻指南

感謝你有興趣貢獻！以下是入門方式。

## 開發環境設定

```bash
git clone https://github.com/claude-world/claude-101.git
cd claude-101
pip install -e ".[all]"
pip install pytest ruff
```

## 執行測試

```bash
# 全部測試
pytest

# 特定測試檔
pytest tests/test_writing.py -v

# 單一測試
pytest tests/test_cli.py::TestToolDispatch::test_draft_email -v
```

## 程式碼風格

- **Linter：** `ruff check src/`
- **型別標註：** 所有公開函式必須有完整 type hints
- **文件字串：** Google 風格，包含 `Args:` 和 `Returns:` 區段
- **無新依賴** — 除非絕對必要，優先使用標準函式庫

## 新增工具流程

1. 在對應模組建立函式（`writing/`、`analysis/`、`coding/`、`business/`）
2. 函式要求：
   - 接受有型別標註的參數，回傳 `dict`
   - 執行**真實計算**（不只是回傳模板）
   - Google 風格文件字串，含 `Args:` 和 `Returns:`
3. 在 `server.py` 用 `@mcp.tool()` 註冊包裝函式
4. 在 `cli.py` 的 `_build_registry()` 中加入登錄
5. 在對應測試檔新增測試
6. 更新 `README.md` 和 `README.zh-TW.md` 的工具數量

## Pull Request 流程

1. Fork 此 repo，從 `main` 建立功能分支
2. 實作變更並加入測試
3. 確認所有測試通過：`pytest`
4. 確認 lint 通過：`ruff check src/`
5. 對 `main` 開 PR，附上清楚的描述

## Commit 訊息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新增情感分析工具
fix: 修正短文的 Flesch 分數計算
docs: 更新 CLI 使用範例
test: 為 formality_score 新增邊界測試
```

## 回報問題

- 使用 GitHub Issues
- 請包含：Python 版本、作業系統、重現步驟、預期 vs 實際行為
- 工具 bug：請附上完整的輸入和輸出 JSON

## 授權

貢獻即代表您同意您的貢獻將以 MIT 授權條款釋出。
