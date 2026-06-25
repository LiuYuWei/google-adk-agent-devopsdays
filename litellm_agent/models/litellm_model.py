import os
from google.adk.models.lite_llm import LiteLlm

# 取得 LiteLLM 模型名稱
model_name = os.getenv("LITELLM_MODEL", "gemini/gemma-4-31b-it")

# 建立 LiteLlm 實體
litellm_gemma_model = LiteLlm(model=model_name)
