# Google ADK Agent Template

這是一個基於 Google ADK (Agent Development Kit) 的專案範本，旨在提供一個標準化的架構，讓開發者可以快速建立、測試並部署 AI Agent。

## 專案特點

- **雙引擎支援**: 內建 `gemini_agent` (原生 Google Gemini) 與 `litellm_agent` (透過 LiteLLM 支援 OpenAI, Anthropic 等)。
- **結構化開發**: 透過資料夾結構管理 `tools` (工具)、`models` (模型)、`instruction` (指令) 與 `skills` (情境技能包)。
- **Skills 整合範例**: 依 [Agent Skill 規範](https://agentskills.io/specification) 內建兩個風格不同的範例 Skill，示範如何將指令、參考資料與工具打包成可動態載入的技能：
  - `gemini_agent/skills/taiwan-travel/`: 純知識型 Skill，搭配 `references/` 提供台灣縣市與美食資料。
  - `litellm_agent/skills/timezone-helper/`: 工具搭配型 Skill，引導 LLM 把使用者輸入轉換為 IANA 時區字串後再呼叫 `get_current_time` 工具。
  - 兩個 agent 故意各放一個不同情境的 Skill，方便互相比對學習。
- **時區工具範例**: 內建支援全球時區轉換的 `get_current_time` 工具，展示如何開發具備參數輸入的工具。
- **Makefile 自動化**: 提供 `make setup` 一鍵初始化環境，自動處理虛擬環境與 `.env` 配置。

## 快速開始

1. **一鍵初始化**:
   此指令會建立虛擬環境、自動從 `.env.template` 複製 `.env` 並安裝所有套件。
   ```bash
   make setup
   ```

2. **配置環境變數**:
   編輯各 Agent 資料夾下的 `.env` 檔案，填入您的 API Key 或 Vertex AI 設定。

3. **啟動 Agent**:
   ```bash
   make run
   ```
   啟動後會出現網址（預設為 http://localhost:8000），點開即可與 AI 助理聊天。

## 目錄結構

- `gemini_agent/`: 使用 Google Gemini 原生驅動的 Agent 實作。
- `litellm_agent/`: 使用 LiteLLM 驅動的通用 Agent (支援 OpenAI, Claude 等)。
  - `tools/sample_tool.py`: 存放工具函式 (如時區查詢)。
  - `models/default.py`: 模型初始化配置。
  - `instruction/system.md`: 系統提示詞。
  - `skills/<skill-name>/SKILL.md`: 依 Agent Skill 規範撰寫的情境技能包，可帶 `references/`、`assets/`、`scripts/`。
  - `.env.template`: 該 Agent 專用的環境變數範本。

## 開發指南

- **新增工具**: 在 `tools/sample_tool.py` 中新增 function，並在 `agent.py` 的 `Agent(tools=[...])` 清單中與 `SkillToolset` 並列註冊。
- **新增 Skills**: 在 `skills/` 下建立子資料夾並撰寫 `SKILL.md` 即可，`agent.py` 會自動掃描載入。詳見 `document/05-develop.md`。
- **修改指令**: 編輯 `instruction/system.md` 檔案即可即時生效。
- **Vertex AI 支援**: 
  在 `.env` 中設定 `GOOGLE_GENAI_USE_VERTEXAI=1` 即可切換至 Vertex AI 模式。

## 常見 Makefile 指令

- `make setup`: 完整環境初始化。
- `make init-env`: 僅初始化 `.env` 檔案。
- `make clean`: 清除快取與暫存檔案。
