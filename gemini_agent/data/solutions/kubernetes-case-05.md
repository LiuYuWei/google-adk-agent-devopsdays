# 解答 — 情境 05：analytics-worker 永遠 Pending 無法排程

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `analytics-worker` 的 Pod 一直是 `0/1`、狀態 `Pending`，`RESTARTS` 為 0、`AGE` 持續增加。
- `kubectl get pods -o wide` 顯示這顆 Pod 的 `NODE` 欄位是 `<none>`，從沒被指派到任何節點；其他服務都正常 Running。

## 🔎 診斷線索（按順序）
1. `status.txt` → `Pending` 且 `RESTARTS=0`、`NODE=<none>`，三個節點都是 `Ready`（不是節點掛掉）。
2. **關鍵在 `describe.txt`**：容器沒有 `State`、`Conditions` 只有 `PodScheduled: False`，Events 出現
   `Warning FailedScheduling ... 0/3 nodes are available: 3 Insufficient cpu ...`。
   - 同時看到 `Requests cpu: 8`、`Node-Selectors: disktype=ssd`。
3. `logs.txt` → Pending 階段沒有應用日誌（`kubectl logs` 回 BadRequest）。**這類問題不要找 logs，要看排程事件**。
4. `events.txt` 進階查證：
   - `kubectl describe node` 顯示單節點 `Allocatable cpu: 3920m`，且已被用掉約 `2500m`，剩約 `1420m`。
   - `kubectl get nodes -L disktype` 顯示所有節點 `DISKTYPE` 都是 `<none>`。

## 🎯 根本原因
容器的 `resources.requests.cpu` 設成 `8`（8 核 = 8000m），**超過任何單一節點可配置的 CPU**（每節點約 3920m，且還有既有服務佔用）。scheduler 以 `requests` 為排程依據，找不到任何容納得下的節點 → Pod 永遠 `Pending`（`FailedScheduling: Insufficient cpu`）。屬於**資源請求設定錯誤**，不是程式或映像檔 bug。

次要因素：`nodeSelector: disktype=ssd` 在叢集中沒有對應節點，事件裡的 `didn't match Pod's node affinity/selector` 就是它造成的。即使把 CPU 修好，只要這個 nodeSelector 還在、又沒有節點貼上 `disktype=ssd`，Pod 一樣排不上。

## ✅ 修正方式

### ① 把 CPU 請求調回合理值（最直接、本情境主因）
批次運算用不到 8 核，調成 1~2 核即可被排程：

```yaml
          resources:
            requests:
              cpu: "1"        # ← 由 8 調回合理值
              memory: 2Gi
            limits:
              cpu: "2"        # limit 是執行上限，可比 request 大
              memory: 2Gi
```

### ② 移除或修正 nodeSelector（次要因素）
叢集沒有 SSD 專用節點，直接移除這段；若日後真有 SSD 節點，再保留並替節點貼 label（`kubectl label node <node> disktype=ssd`）：

```yaml
    spec:
      # nodeSelector:        # ← 整段移除（或在真有 SSD 節點時才保留）
      #   disktype: ssd
      containers:
        - name: analytics-worker
```

### ③ 若工作負載真的需要 8 核
那就不是改 YAML，而是要擴大節點規格／新增更大機型的 node pool（例如 e2-standard-8 以上），再用 `nodeSelector` 或 `nodeAffinity` 指定排到大機型節點。

修正後套用並驗證：

```bash
kubectl apply -f manifest.yaml
kubectl get pods -n shopnow -l app=analytics-worker -w
# 應由 Pending 轉為 ContainerCreating，最後變成 1/1 Running：
# NAME                                READY   STATUS    RESTARTS   AGE
# analytics-worker-9b6f7c5d83-n4t2k   1/1     Running   0          22s
```

## 🧠 延伸重點
- `Pending` 的常見原因清單（看到 Pending 先逐項排查）：
  1. **資源不足**：`requests.cpu` / `requests.memory` 太大，沒有節點塞得下（本情境）。
  2. **nodeSelector / nodeAffinity 不符**：指定的 label 沒有任何節點符合。
  3. **taint 未容忍**：節點有 taint，但 Pod 沒對應的 toleration。
  4. **PVC 無法綁定**：要掛的 PersistentVolumeClaim 找不到可用的 PV / StorageClass。
  5. **節點數量不足 / 都不可排程**：節點被 cordon、或叢集根本沒有可用節點。
- `requests` 是 **排程依據**（scheduler 用它決定塞不塞得進去）；`limits` 是 **執行上限**（容器跑起來後最多能用多少）。兩者意義不同，排程只看 request。
- 排查 Pending 的標準動作：`kubectl describe pod` 看 `FailedScheduling` 事件，再用 `kubectl describe nodes` 比對 `Allocatable`（節點能給多少）與 `Allocated resources`（已經用掉多少），就能判斷「是不是真的塞不下」。
- 與 `case-01`、`case-03` 對照：那兩個是「容器有起來、但程式崩潰或被殺」（執行階段問題）；這個是「容器根本沒被排到節點上」（排程階段問題），所以 `logs` 一定是空的。
