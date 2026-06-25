---
title: 環境準備與初始化
duration: 15
---

# 2. 環境準備與初始化

本工作坊強烈建議使用 **Google Cloud Console (Cloud Shell)** 進行。

### 必備條件
1.  **Google Cloud 帳號**: 您需要一個具備帳單帳戶的 GCP 專案。
2.  **啟用 Cloud Shell**: 登入 [Google Cloud Console](https://console.cloud.google.com/) 並點擊右上角的「啟用 Cloud Shell」。

### 複製專案與安裝工具
在 Cloud Shell 終端機中，執行以下指令：

```bash
# 複製專案
git clone https://github.com/LiuYuWei/google-adk-agent-template.git
cd google-adk-agent-template

# 安裝自動化設定工具
pip install bwai-workshop-tools
```

---

### 執行自動化初始化 (Setup)

我們將使用 `bwai-workshop-tools` 來處理繁瑣的認證、API 啟用與環境建立：

```bash
bwai-workshop setup --step environment/bwai_env_config.json
```

執行過程中，系統會引導您完成 **GCP 登入**、**專案選取** 與 **Gemini CLI 認證**。

### 驗證與啟動環境
設定完成後，請執行驗證確保一切就緒，並手動啟動虛擬環境：

```bash
# 驗證設定
bwai-workshop verify --step environment/bwai_env_config.json

# 啟動虛擬環境
source .venv/bin/activate
```

---

### 使用 Gemini CLI 協助

您也可以隨時啟動 **Gemini CLI**，要求它解釋專案結構或協助開發工具：

```bash
gemini "請向我解釋這個 ADK 專案的運作方式"
```

> [!TIP]
> 確保已執行 `source .venv/bin/activate`，否則後續指令可能會因為找不到套件而失敗。
