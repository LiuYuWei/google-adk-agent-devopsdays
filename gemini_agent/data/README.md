# 📦 DevOpsDays 模擬故障資料集（k8s / docker）

這個資料夾收錄一組**很真實的模擬故障情境**，給課程學員練習：用 Agent / 自製工具**查詢 log → 診斷根因 → 模擬修正** k8s 與 docker 問題。

> 所有資料皆為**模擬**，公司名稱（shopnow）、映像檔、IP、密碼皆為虛構，可安全公開使用。

---

## 🧱 固定資料夾格式（學員寫工具的契約）

**每一個 case 資料夾，都包含完全相同的 6 個檔案、相同檔名。**
學員只要針對「一種資料夾格式」寫查詢工具，就能套用到所有情境。

| 檔名 | 角色 | Kubernetes 情境 | Docker 情境 |
| :--- | :--- | :--- | :--- |
| `metadata.json` | 情境索引（機器可讀） | id / 平台 / 服務 / 難度 | 同左 |
| `status.txt` | 資源狀態總覽 | `kubectl get pods` | `docker ps -a` |
| `describe.txt` | 詳細資訊 | `kubectl describe pod` | `docker inspect` |
| `logs.txt` | 容器 / 應用日誌 | `kubectl logs`（含 `--previous`） | `docker logs` |
| `events.txt` | 事件與輔助診斷 | `kubectl get events` + 進階查證 | daemon 訊息 / build log |
| `manifest.yaml` | 部署設定 | Deployment YAML | docker-compose.yaml |

> 💡 **`metadata.json` 的固定欄位**：`id`、`platform`、`workload`、`difficulty`、`files`（檔案清單）；k8s 另含 `namespace`。
> 工具可先讀 `metadata.json` 做索引，再依需求讀其他檔案。

### 🙈 故意「不暴雷」的兩個設計
1. **資料夾名稱是中性的**（`case-01`、`case-02`…），**光看路徑無法得知是什麼錯誤**。`metadata.json` 也刻意**不放故障類型或根因**——避免在 agent 查到資料前就洩題。
2. **原始資料檔（`status.txt` / `describe.txt` / `logs.txt` / `events.txt` / `manifest.yaml`）一律「無註解」**：完全是擬真的 kubectl / docker 原始輸出，bug 自然藏在資料裡但**不標示問題在哪**，讓 Agent 自己從 log 推斷根因——這才是真實的故障排除 showcase。

> 每個 `.txt` 檔開頭都保留了原始 `$ <command>` 提示符，方便工具用關鍵字（如 `CrashLoopBackOff`、`OOMKilled`、`Exit Code 137`）做 grep / 全文搜尋。

### 📝 解答放哪裡？
**講師解答卷集中在 [`solutions/`](./solutions/)**（不在 case 資料夾內），檔名對應 case：`solutions/kubernetes-case-01.md`、`solutions/docker-case-04.md`…
做 showcase 時，**請讓工具只掃描 `kubernetes/` 與 `docker/` 下的 case 資料夾、不要讀 `solutions/`**，Agent 才不會直接看到答案。

---

## 🗂️ 情境清單（中性）

> 故障類型與根因請見 [`solutions/README.md`](./solutions/README.md)（講師用）。

### Kubernetes（`kubernetes/case-0X/`）
| 案例 | 受影響服務 | 難度 |
| :--- | :--- | :--- |
| `case-01` | payment-api | 入門 |
| `case-02` | order-service | 入門 |
| `case-03` | recommendation-engine | 中階 |
| `case-04` | email-worker | 入門 |
| `case-05` | analytics-worker | 中階 |
| `case-06` | notification-service | 中階 |

### Docker（`docker/case-0X/`）
| 案例 | 受影響服務 | 難度 |
| :--- | :--- | :--- |
| `case-01` | shopnow-api | 入門 |
| `case-02` | shopnow-frontend | 入門 |
| `case-03` | shopnow-report-gen | 中階 |
| `case-04` | shopnow-image-processor | 中階 |

---

## 🎓 建議的課堂流程
1. 學員寫一個讀取「固定資料夾格式」的工具（例如 `read_incident(platform, case_id, file)`）。
2. 把工具註冊進 `gemini_agent` / `litellm_agent`（見專案根目錄 `CLAUDE.md`）。
3. 丟一個 case（例如 `kubernetes/case-03`）給 Agent，請它：① 讀 log → ② 指出根因 → ③ 產出修正後的 `manifest.yaml`。
4. 講師對照 `solutions/<platform>-case-0X.md` 驗收。
