---
title: 配置環境變數
duration: 5
---

# 3. 配置環境變數

在完成第 3 步的自動化初始化後，系統已經為您從範本產生了各個 Agent 的 `.env` 檔案。現在我們需要設定正確的專案資訊。

### 在 Cloud Shell 中編輯
點擊 Cloud Shell 工具列上的「開啟編輯器」按鈕（圖示為鉛筆），這會開啟一個類似 VS Code 的介面。

### 設定 Gemini Agent
在編輯器左側導覽列找到 `gemini_agent/.env` 並開啟。確保填入您的 Google Cloud 資訊：

```env
# Vertex AI Configuration
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=<您的 GCP 專案 ID>
GOOGLE_CLOUD_LOCATION=us-central1

# Gemini Model Name
GEMINI_MODEL=gemini-2.5-flash
```

> **重要**: 即使自動化工具已嘗試設定，請務必手動確認 `GOOGLE_CLOUD_PROJECT` 是否正確。

