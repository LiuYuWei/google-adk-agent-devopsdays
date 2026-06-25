---
title: 自定義開發
duration: 15
---

# 5. 自定義開發

ADK 的強大之處在於其結構化的開發方式。除了傳統的 **Tools (工具)** 之外，ADK 也支援 **Skills (情境技能包)**，讓您能將指令、參考資料與工具一起封裝為可動態載入的模組。

---

## 修改系統指令
編輯 `gemini_agent/instruction/system.md`。
您可以嘗試將代理設定為「毒舌的工程師」或「溫柔的客服人員」，修改後重新啟動 `make run` 即可見效。

---

## 新增工具 (Tools)
1.  在 `gemini_agent/tools/` 下新增一個 Python 檔案，例如 `weather.py`。
2.  定義一個 function 並加上 Type Hint 與 Docstring。
3.  在 `agent.py` 中匯入新工具，並加入 `Agent(tools=[...])` 清單與 `SkillToolset` 並列（這樣工具會永遠對 LLM 可用）。

### 範例工具代碼：
```python
def get_weather(city: str) -> str:
    """取得指定城市的當前天氣。"""
    return f"{city} 的天氣是晴天，攝氏 25 度。"
```

---

## 新增 Skills (情境技能包)

> Skills 是 ADK 的進階能力，可將「指令 + 參考資料 + 工具」打包成一個可動態載入的單元。當使用者的問題符合 Skill 的描述時，Agent 才會把該 Skill 的指令載入到 context window，避免一次塞入過多訊息。

### Skill 的三層結構
1. **L1 Metadata**：`SKILL.md` 的 frontmatter（`name`、`description`），Agent 用來判斷何時觸發。
2. **L2 Instructions**：`SKILL.md` 的內文，Skill 被觸發時才會載入。
3. **L3 Resources**：`references/`、`assets/`、`scripts/` 下的延伸資源，僅在 Skill 主動讀取時才會被使用。

### 建立步驟
1. 在 `<agent_dir>/skills/` 下新增子資料夾，例如 `gemini_agent/skills/my_skill/`。
2. 建立 `SKILL.md`：
    ```markdown
    ---
    name: my-skill
    description: 一句話說明這個 Skill 的觸發情境（Agent 會以此判斷何時載入）。
    ---

    # 我的 Skill 標題

    ## 工作流程
    1. 步驟 1...
    2. 步驟 2，可讀取 `references/foo.md`...
    3. 步驟 3，呼叫工具 `get_current_time(...)` 並回傳結果。
    ```
3. （選擇性）在 `references/`、`assets/`、`scripts/` 中放入額外的參考資料、範本檔案或腳本。
4. **無須手動註冊**：`agent.py` 已透過 `load_all_skills()` 自動掃描 `skills/` 下所有具備 `SKILL.md` 的子資料夾。
5. 重新執行 `make run`，在 Web UI 提出符合 Skill 描述的問題（例如「我想去花蓮玩」），觀察 Agent 是否載入該 Skill 的指令。

### 內建範例
- `gemini_agent/skills/taiwan_travel/`：台灣旅遊推薦助手，含縣市與美食兩份 references。
- `litellm_agent/skills/timezone_helper/`：時區查詢助手，搭配既有的 `get_current_time` 工具。

### 進一步閱讀
- ADK Skills 官方文件：[Skills for ADK agents](https://google.github.io/adk-docs/)
- Agent Skill 規範：<https://agentskills.io/specification>
