# 解答 — 情境 04：email-worker 卡在 CreateContainerConfigError

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `email-worker` 的 2 個 Pod 都是 `0/1`、狀態 `CreateContainerConfigError`。
- 重點：`RESTARTS` 一直是 `0`。容器**從來沒被建立起來**，所以也談不上「重啟」（這是和 CrashLoopBackOff 最直觀的差別）。

## 🔎 診斷線索（按順序）
1. `status.txt` → `CreateContainerConfigError`、`RESTARTS 0`、AGE 才幾分鐘。
2. `describe.txt` → 容器 `State: Waiting / Reason: CreateContainerConfigError`，`Restart Count: 0`。
   - Environment 區段寫著：`SMTP_PASSWORD: <set to the key 'password' in secret 'smtp-credentials'>  Optional: false`。
   - Events 出現關鍵行：`Warning  Failed  ...  Error: secret "smtp-credentials" not found`（且 `x9` 反覆出現）。
3. `logs.txt` → **沒有應用日誌**，只回 `is waiting to start: CreateContainerConfigError`；`--previous` 也抓不到。診斷重點不在 logs，而在 describe 的 Events。
4. `events.txt` → `kubectl get secret -n shopnow` 證實叢集裡**沒有** `smtp-credentials`（只有 order-db / payment-db / registry-pull 等）。

## 🎯 根本原因
Deployment 的 env 透過 `secretKeyRef` 引用了一個**不存在的 Secret `smtp-credentials`**。kubelet 在建立容器前要先把環境變數組好，但取不到這個 Secret 的 `password` key → 無法組出容器設定 → `CreateContainerConfigError`。容器壓根沒被建立，因此沒有任何程式日誌、RESTARTS 也維持 0。屬於**設定（configuration）問題**，不是程式或映像檔 bug。

## ✅ 修正方式
只要把缺少的 Secret 建立起來即可，**不需要改 Deployment**。Pod 會自動重試並轉為 Running。

方式 A：直接用指令建立（最快）

```bash
kubectl create secret generic smtp-credentials -n shopnow \
  --from-literal=username=email-worker@shopnow.internal \
  --from-literal=password=s3cr3t-smtp-p@ss \
  --from-literal=host=smtp.shopnow.internal
```

方式 B：套用 `manifest.yaml` 裡附的那份 Secret 範例（`---` 之後的第二份文件）

```bash
kubectl apply -f manifest.yaml   # 內含 Secret smtp-credentials 的定義
```

驗證（Pod 會自動重試，不必手動刪 Pod）：

```bash
kubectl get secret smtp-credentials -n shopnow                 # 應看到 smtp-credentials 已存在
kubectl get pods -n shopnow -l app=email-worker                # 應陸續變為 1/1 Running、RESTARTS 0
kubectl rollout status deployment/email-worker -n shopnow
```

## 🧠 延伸重點
- **CreateContainerConfigError vs CrashLoopBackOff**：
  - 這個（ConfigError）：容器**還沒建立**，kubelet 組設定就失敗 → 沒有應用日誌、`RESTARTS` 不會累加（通常維持 0）。
  - CrashLoopBackOff（情境 01）：容器**有建立、有跑**，但程式自己崩潰退出（Exit Code ≠ 0）→ 有 `logs --previous`、`RESTARTS` 一直增加。
- **常見變體**（都會造成 CreateContainerConfigError）：
  - Secret / ConfigMap 的**名字打錯**（例如 `smtp-credential` 少了 s）。
  - 引用的 **key 名字錯**（Secret 存在，但裡面沒有 `password` 這個 key）。
  - Secret **建在錯的 namespace**：Secret 必須與 Pod **同一個 namespace** 才取得到。
  - 把 `secretKeyRef` 改成 `optional: true`，可讓該變數在 Secret 缺失時不硬性失敗（容器照樣起得來，但程式要自己容忍缺值）。
- 排查時請務必確認 **namespace**：`kubectl get secret -n <pod 所在 namespace>`，別在 default 看半天。
