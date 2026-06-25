---
title: 清理資源
duration: 5
---

# 8. 清理資源

在工作坊結束後，為了避免產生不必要的費用，建議您清理在 Google Cloud 上建立的資源。

### 步驟 1：刪除 Cloud Run 服務
執行以下指令來刪除部署的 Agent 服務：

```bash
make destroy PROJECT=your-project-id
```

### 步驟 2：清理本地快取與暫存檔
執行以下指令來清除 Python 的 `__pycache__` 以及 ADK 產生的暫存資料夾：

```bash
make clean
```

### 步驟 3：停用虛擬環境 (選用)
如果您想離開開發環境，可以執行：

```bash
deactivate
```

> **提示**: 如果您未來不再需要此 GCP 專案，也可以直接在 Google Cloud Console 中關閉整個專案。
