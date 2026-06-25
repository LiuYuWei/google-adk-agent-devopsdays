# 🚀 Workshop 實作手冊：從零打造你的 Google ADK Agent

本手冊將帶你一步一步完成 Agent 的開發與部署，建議使用 **Google Cloud Shell** 進行操作。

---

## Step 1：環境準備

### 1-1. 啟動 Cloud Shell
登入 [Google Cloud Console](https://console.cloud.google.com/) 並點擊右上角的「啟用 Cloud Shell」。

### 1-2. 複製專案與安裝工具
```bash
# Clone 專案
git clone https://github.com/LiuYuWei/google-adk-agent-template.git
cd google-adk-agent-template

# 安裝自動化設定工具
pip install bwai-workshop-tools
```

---

## Step 2：自動化環境初始化

我們提供了一鍵設定指令，會自動處理：
*   `gcloud` 登入與專案切換
*   啟用必要 Google Cloud APIs
*   Gemini CLI (Vertex AI) 認證
*   Python 虛擬環境建立與套件安裝

```bash
# 執行自動化設定
bwai-workshop setup --step environment/bwai_env_config.json

# 啟動虛擬環境 (此步驟必須手動執行)
source .venv/bin/activate
```

> **驗證**: 若想確認環境是否準備好，可執行 `bwai-workshop verify --step environment/bwai_env_config.json`。

---

## Step 3：配置環境變數 (.env)

使用 Cloud Shell 編輯器打開 `gemini_agent/.env`，確保內容包含以下資訊：

```dotenv
# Vertex AI Configuration
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id       # 確認此處為您的 GCP 專案 ID
GOOGLE_CLOUD_LOCATION=us-central1

# Gemini Model Name
GEMINI_MODEL=gemini-2.5-flash
```

---

## Step 4：本地啟動與測試

### 4-1. 啟動伺服器
```bash
make run
```

### 4-2. 網頁預覽
點擊 Cloud Shell 右上角的 **「網頁預覽」** ➡️ **「在通訊埠 8000 上進行預覽」**。

> 您應該能看到 ADK 的對話介面。確認可以正常對話後，按 `Ctrl+C` 停止伺服器。

---

## Step 5：自訂開發 (開發重點)

### 5-1. 修改角色指令 (System Instruction)
編輯 `gemini_agent/instruction/system.md`，定義你的 Agent 角色（例如：毒舌工程師、專業理財專員等）。

### 5-2. 新增工具 (Tools)
在 `gemini_agent/tools/` 新增 Python 檔案，並在 `gemini_agent/agent.py` 中匯入並註冊至 `tools` 列表。

---

## Step 6：部署到 Google Cloud Run

```bash
# 一鍵部署至雲端
make deploy PROJECT=$(gcloud config get-value project)
```

部署完成後，使用輸出中的 **Service URL** 即可從公開網路存取。

---

## 常見問題

| 問題 | 解法 |
| :--- | :--- |
| `make run` 報錯或找不到模組 | 確認已執行 `source .venv/bin/activate` |
| 網頁預覽出現 404 | 確認 `make run` 指令已啟動完成，且使用的是 8000 通訊埠 |
| 部署權限不足 | 確認您的帳號具有 `Owner` 或 `Cloud Run Admin` 權限 |

