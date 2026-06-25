---
title: 部署至 Cloud Run
duration: 5
---

# 6. 部署至 Cloud Run

環境驗證與測試完成後，您可以將 AI 代理正式部署到雲端。

### 一鍵部署
在終端機中執行以下指令（系統會自動讀取您目前的 GCP 專案）：

```bash
make deploy PROJECT=$(gcloud config get-value project)
```

### 部署完成
部署流程約需 2-3 分鐘。完成後，終端機會輸出一組 `Service URL`。您可以點擊該連結直接在瀏覽器中存取您的代理服務。

### 管理您的服務
您也可以前往 [Cloud Run 控制台](https://console.cloud.google.com/run) 查看服務狀態、日誌與管理設定。

