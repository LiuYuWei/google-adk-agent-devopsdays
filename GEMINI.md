# 🧠 Gemini CLI 開發與維護指令手冊 (通用規範)

這份文件是給 **Gemini CLI (AI Agent)** 的核心行動準則。請協助使用者開發與管理專案中的各個 Agent（如 `gemini_agent/`、`litellm_agent/` 或自定義資料夾）。

---

## 📍 1. 識別目標：我該修改哪個資料夾？

當使用者提出需求時，請先判斷目標 Agent 資料夾（以下標記為 `<agent_dir>`）：
- 如果指令提到 **Gemini**：對應 `gemini_agent/`。
- 如果指令提到 **LiteLLM/萬用/其他模型**：對應 `litellm_agent/`。
- 如果使用者已**建立新 Agent**：請先列出目錄確認資料夾名稱。

---

## 🗺️ 2. 專案地圖：該去哪裡修改？

請根據 `<agent_dir>` 決定具體路徑：

| 使用者需求 | 對應操作路徑 | 修改重點 |
| :--- | :--- | :--- |
| **「修改 AI 的性格或指令」** | `<agent_dir>/instruction/system.md` | 調整 AI 的角色定義與規範。 |
| **「增加或修改功能工具 (Tools)」** | `<agent_dir>/tools/sample_tool.py` | 撰寫 Python 邏輯並提供繁體中文 Docstring。 |
| **「新增/修改 Skills（情境技能包）」** | `<agent_dir>/skills/<skill-name>/` | 撰寫 `SKILL.md` 與 `references/`，依 Agent Skill 規範組織。 |
| **「更換模型版本」** | `<agent_dir>/models/default.py` | 更新模型字串（如 `gemini-2.5-flash`）。 |
| **「註冊或管理工具/Skills 清單」** | `<agent_dir>/agent.py` | 在 `SkillToolset` 的 `additional_tools` / `skills` 中增減內容；Skills 由 `load_all_skills()` 自動掃描。 |
| **「設定金鑰 (API Key) 或環境參數」** | `<agent_dir>/.env` | **填寫或修正金鑰、專案 ID 等設定。** |

---

## 🛠️ 3. 標準開發流程 (核心規範)

> ⚠️ **重要優先準則**：在進行任何代碼修改或執行之前，請務必先確認環境已就緒。

1. **環境初始化與金鑰設定 (優先執行)**：
   - 當使用者提到「準備環境」或「第一次啟動」時，**執行 `make setup`**。
   - **接著，主動協助使用者修改 `<agent_dir>/.env` 檔案**，填入對應的 API Key、Google Cloud 專案 ID 或時區等必要參數。
2. **目錄探索**：不確定目標時，先執行 `ls -d */` 查看現有的 Agent 資料夾。
3. **新增工具 (Tools) 的標準流程**：
   - **Step A**：在 `<agent_dir>/tools/` 新增 Python 函式，並撰寫完整的繁體中文 Docstring（Docstring 決定 Agent 何時呼叫此工具）。
   - **Step B**：在 `<agent_dir>/agent.py` 的頂部 import 新工具，並加入 `Agent(tools=[...])` 清單與 SkillToolset 並列（這樣工具會永遠暴露給 LLM）。
   - 每次修改後提醒使用者執行 `make run` 進行測試。
4. **新增 Skills (情境技能包) 的標準流程**：
   - **Step A**：在 `<agent_dir>/skills/<skill-name>/` 建立資料夾。
   - **Step B**：撰寫必要檔案 `SKILL.md`（frontmatter 內含 `name` 與 `description` — Agent 會以此判斷何時觸發 Skill），並視需要新增 `references/`、`assets/`、`scripts/` 子資料夾。
   - **Step C**：`agent.py` 中的 `load_all_skills()` 會自動掃描 `skills/` 下的子資料夾，**不需要手動註冊**；只要 `SKILL.md` 存在即可生效。
   - Skill 規範請參考 [Agent Skill 規範文件](https://agentskills.io/specification)。
5. **部署至 Google Cloud Run**：
   - 使用 `adk deploy cloud_run` 指令（ADK CLI 內建）進行部署，**不需要手動撰寫 Dockerfile 或 gcloud 指令**。
   - 標準部署指令：`make deploy PROJECT=<gcp-project-id>`
   - 此指令會自動打包 `gemini_agent/` 並部署至 Cloud Run，同時啟用 Web UI（`--with_ui`）。
   - 部署前確認使用者已執行：`gcloud auth login` 與 `gcloud auth application-default login`。
6. **代碼實作規範**：
   - 務必在 Python 檔案中加入**繁體中文註解**。
   - 本機測試：執行 `make run`，開啟 `http://localhost:8000`。
   - 雲端測試：執行 `make deploy PROJECT=xxx`，部署完成後使用輸出的 Service URL 存取。

---

## 🎨 4. 台灣習慣規範

- **中文優先**：所有 Docstring、註解、錯誤訊息皆須使用台灣繁體中文。
- **白話翻譯**：自動將使用者的口語需求（如「我想讓它會算數學」）轉化為對應的技術實作。

---

**給 Gemini CLI 的提醒**：你是使用者的專業開發助手，除了寫程式，**請務必協助使用者搞定 `.env` 的設定**，這是 Agent 能否成功連線並運行的關鍵。
