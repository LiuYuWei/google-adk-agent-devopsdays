import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import skill_toolset

# 1. 載入工具 (從 tools/ 內直接填入要使用的名稱)
from .tools.sample_tool import get_current_time

# 2. 載入環境變數
load_dotenv()

# 3. 設定模型 (從 models/ 資料夾引入)
from .models.gemini_model import gemini_model

# 4. 載入指令 (從 instruction/ 資料夾引入)
from .instruction import system_instruction

# 5. 載入 Skills (從 skills/ 資料夾引入)
from .skills import load_all_skills

# 6. 將 Skills 包裝成 SkillToolset，由 LLM 視情境動態載入
agent_toolset = skill_toolset.SkillToolset(
    skills=load_all_skills(),
)

# 7. 定義 Agent
#    - SkillToolset 負責管理 skills（list / load / load_resource / run_script）。
#    - 一般工具 (例如 get_current_time) 直接放在 tools 列表中，永遠對 LLM 可用。
root_agent = Agent(
    name='gemini_root_agent',
    model=gemini_model,
    instruction=system_instruction,
    description='這是一個可以用來練習的 Google Gemini Agent 範本。',
    tools=[
        agent_toolset,      # Skills（情境技能包）
        get_current_time,   # 全域工具（一律可用）
    ]
)
