# 🧠 Claude Code 開發與維護指令手冊 (通用規範)

本文件是給 **Claude Code (AI Agent)** 的核心行動手冊。請依照使用者的中文指令，彈性地管理專案中的 Agent 資料夾（如 `gemini_agent/`、`litellm_agent/` 或使用者自定義的資料夾）。

---

## 📍 1. 識別目標：修改哪個資料夾？

在收到改動指令時，請先根據上下文識別目標資料夾（`<agent_dir>`）：
- **關鍵字：Gemini** ➡️ `gemini_agent/`。
- **關鍵字：LiteLLM/GPT/Claude/萬用** ➡️ `litellm_agent/`。
- **無明確說明**：先執行 `ls` 確認現有 Agent 目錄，或詢營使用者。

---

## 🗺️ 2. 專案地圖：該去哪裡修改？

請根據 `<agent_dir>` 路徑定位：

| 使用者需求 | 對應操作路徑 | 修改建議 |
| :--- | :--- | :--- |
| **「修改角色指令、行為或性格」** | `<agent_dir>/instruction/system.md` | 調整核心提示詞 (Prompt)。 |
| **「開發或改動 Python 工具 (Tools)」** | `<agent_dir>/tools/sample_tool.py` | 撰寫函式邏輯並提供繁體中文註解。 |
| **「新增/修改 Skills（情境技能包）」** | `<agent_dir>/skills/<skill-name>/` | 撰寫 `SKILL.md` 與 `references/`，依 Agent Skill 規範組織。 |
| **「調整模型版本或供應商」** | `<agent_dir>/models/default.py` | 更新模型初始化設定。 |
| **「註冊工具至 Agent 的實例中」** | `<agent_dir>/agent.py` | 管理 `SkillToolset` 中的 `skills` 與 `additional_tools`。 |
| **「設定金鑰 (API Key) 或環境參數」** | `<agent_dir>/.env` | **填寫或修改金鑰、專案 ID 等設定。** |

---

## 🛠️ 3. Agent 開發工作流 (核心規範)

> ⚠️ **重要優先準則**：所有開發工作必須建立在已完成初始化環境的基礎之上。

1. **優先處理環境與金鑰 (First Priority)**：
   - 使用者提到「準備環境」或環境尚未初始化時，**務必執行 `make setup`**。
   - **隨後，應主動確認並協助使用者修改 `<agent_dir>/.env`**，將範本中的佔位符替換為實際的 API Key 或雲端專案資訊。
2. **分析與開發**：
   - 根據指令分析該改動哪個檔案。
   - 所有代碼變動後，請檢查 `agent.py` 的匯入路徑是否正確。
3. **新增工具 (Tools) 的標準流程**：
   - **Step A**：在 `<agent_dir>/tools/` 新增 Python 函式，並撰寫完整的繁體中文 Docstring（Docstring 決定 Agent 何時呼叫此工具）。
   - **Step B**：在 `<agent_dir>/agent.py` 的頂部 import 新工具，並加入 `Agent(tools=[...])` 清單與 SkillToolset 並列（這樣工具會永遠暴露給 LLM）。
   - 每次修改後提醒使用者執行 `make run` 進行測試。
4. **新增 Skills (情境技能包) 的標準流程**：
   - **Step A**：在 `<agent_dir>/skills/<skill-name>/` 建立資料夾。
   - **Step B**：撰寫必要檔案 `SKILL.md`（frontmatter 內含 `name` 與 `description` — Agent 會以此判斷何時觸發 Skill），並視需要新增 `references/`、`assets/`、`scripts/` 子資料夾。
   - **Step C**：`agent.py` 中的 `load_all_skills()` 會自動掃描 `skills/` 下的子資料夾，**不需要手動註冊**；只要 `SKILL.md` 存在即可生效。
   - 每次修改後提醒使用者執行 `make run` 進行測試。
5. **部署至 Google Cloud Run**：
   - 使用 `adk deploy cloud_run` 指令（ADK CLI 內建）進行部署，**不需要手動撰寫 Dockerfile 或 gcloud 指令**。
   - 標準部署指令：`make deploy PROJECT=<gcp-project-id>`
   - 此指令會自動打包 `gemini_agent/` 並部署至 Cloud Run，同時啟用 Web UI（`--with_ui`）。
   - 部署前確認使用者已執行：`gcloud auth login` 與 `gcloud auth application-default login`。
6. **完成與測試**：
   - 本機測試：執行 `make run`，開啟 `http://localhost:8000`。
   - 雲端測試：執行 `make deploy PROJECT=xxx`，部署完成後使用輸出的 Service URL 存取。

---

## 🎨 4. 台灣繁體中文規範

- **口語與註解**：所有的對話、Docstring 與註解皆應使用台灣繁體中文，保持友善且白話。
- **工具描述**：確保 Docstring 內容詳盡，因為它決定了終端使用者在介面上看到的說明。

---

**給 Claude Code 的提醒**：使用者將依賴你進行技術實作。**請將 `make setup` 與 `.env` 的設定視為首要任務**，確保 Agent 在連線無誤的狀態下開發與運行。
