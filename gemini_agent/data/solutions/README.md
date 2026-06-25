# 🔑 解答索引（講師用）

> ⚠️ **這個資料夾是答案卷**。做 Agent showcase 時，請**不要**把 `solutions/` 放進工具的查詢範圍，避免 Agent 直接看到根因。
> 對應關係：`solutions/<platform>-case-0X.md` ↔ `../<platform>/case-0X/`。

## Kubernetes
| 案例 | 受影響服務 | 表面狀態 | 根本原因（一句話） |
| :--- | :--- | :--- | :--- |
| [kubernetes-case-01](./kubernetes-case-01.md) | payment-api | CrashLoopBackOff | Deployment 缺少必填環境變數 `DATABASE_URL`，程式啟動即崩潰（Exit 1） |
| [kubernetes-case-02](./kubernetes-case-02.md) | order-service | ImagePullBackOff | 指定了不存在的映像檔 tag（`1.8.0`），registry 最新只有 `1.7.3` |
| [kubernetes-case-03](./kubernetes-case-03.md) | recommendation-engine | OOMKilled (137) | memory limit 512Mi 太低 + `-Xmx` 寫死沒留堆外空間，被 cgroup OOM 砍掉 |
| [kubernetes-case-04](./kubernetes-case-04.md) | email-worker | CreateContainerConfigError | `secretKeyRef` 引用了不存在的 Secret `smtp-credentials`，容器建不起來 |
| [kubernetes-case-05](./kubernetes-case-05.md) | analytics-worker | Pending | `requests.cpu: 8` 超過任何單節點可配置 CPU（另有 `nodeSelector` 無對應節點） |
| [kubernetes-case-06](./kubernetes-case-06.md) | notification-service | Running 但反覆重啟 | livenessProbe 路徑設成 `/health`（404），應為 `/healthz`，健康容器被誤殺（Exit 143） |

## Docker
| 案例 | 受影響服務 | 表面狀態 | 根本原因（一句話） |
| :--- | :--- | :--- | :--- |
| [docker-case-01](./docker-case-01.md) | shopnow-api | Exited (1) | 缺少必填環境變數 `JWT_SECRET`，容器啟動即退出 |
| [docker-case-02](./docker-case-02.md) | shopnow-frontend | 啟動失敗 (bind error) | host port 8080 已被既有容器 `legacy-dashboard` 占用，port is already allocated |
| [docker-case-03](./docker-case-03.md) | shopnow-report-gen | build 失敗 | `requirements.txt` 釘了不存在的版本 `pandas==99.9.9`，`pip install` 中止 |
| [docker-case-04](./docker-case-04.md) | shopnow-image-processor | Exited (137) | 容器 `mem_limit: 256m` 太低，處理大圖時超用被 OOM killer SIGKILL |
