import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools import skill_toolset

# 1. 載入自定義工具 (Tools)
from .tools.sample_tool import get_current_time

# 2. 基礎配置
load_dotenv()

# 3. 載入模型 (Model) 與 指令 (Instruction)
from .models.litellm_model import litellm_gemma_model
from .instruction import system_instruction

# 4. 載入 Skills (從 skills/ 資料夾引入)
from .skills import load_all_skills

# 5. 將 Skills 包裝成 SkillToolset，由 LLM 視情境動態載入
agent_toolset = skill_toolset.SkillToolset(
    skills=load_all_skills(),
)

# 6. 定義 ADK Root Agent
#    - SkillToolset 管理 skills（list / load / load_resource / run_script）。
#    - 一般工具 (例如 get_current_time) 直接放在 tools 列表中，永遠對 LLM 可用。
root_agent = Agent(
    name='litellm_root_agent',
    model=litellm_gemma_model,
    instruction=system_instruction,
    description='這是一個可以用來練習的通用 Agent 範本，支援多種 LLM 供應商。',
    tools=[
        agent_toolset,      # Skills（情境技能包）
        get_current_time,   # 全域工具（一律可用）
    ]
)
