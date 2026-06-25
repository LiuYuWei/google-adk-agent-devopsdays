# 解答 — 情境 06：notification-service 表面 Running 卻反覆重啟

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `notification-service` 的 2 個 Pod 都是 `1/1 Running`，看起來很正常，但 `RESTARTS` 一路飆到 7、8，而且 `(45s ago)` 代表「剛剛才又重啟過一次」。
- AGE 才 32 分鐘卻重啟 8 次，平均每隔幾分鐘就被殺一次——典型的「假死」：每次都是啟動沒多久就被終止。
- 應用日誌裡完全沒有 error / crash，程式其實是健康的。

## 🔎 診斷線索（按順序）
1. `status.txt` → `STATUS` 是 `Running`、`READY` 是 `1/1`，但 `RESTARTS` 不斷增加且剛剛才重啟。和 CrashLoopBackOff 不一樣，這裡沒有 `0/1`。
2. `describe.txt` → 容器目前 `State: Running`，但 `Last State: Terminated / Reason: Error / Exit Code: 143`。**143 = 128 + 15（SIGTERM）**，代表是「被 kubelet 主動送 SIGTERM 終止」，不是程式自己崩潰。
3. `describe.txt` 的 Events 反覆出現兩行關鍵訊息：
   - `Warning  Unhealthy  ... Liveness probe failed: HTTP probe failed with statuscode: 404`
   - `Normal   Killing    ... Container notification-service failed liveness probe, will be restarted`
   - 同時注意：Liveness 探針路徑是 `/health`，而 Readiness 探針路徑是 `/healthz`，兩者不一致。
4. `logs.txt` → 應用正常啟動（`notification-service listening on :8084`、`health endpoint registered at /healthz`），接著收到一連串 `GET /health 404`，最後 `Received SIGTERM, shutting down gracefully...`。`--previous` 顯示每一輪都是同樣的劇本。
5. `events.txt` → 直接打端點驗證：`/health` 回 `404`、`/healthz` 回 `200`；再用 jsonpath 撈出 livenessProbe 路徑確認是 `/health`。

## 🎯 根本原因
Deployment 的 **livenessProbe 路徑設成 `/health`（少了 z），這個路徑在應用裡不存在，會回 404**。而應用真正的健康端點是 `/healthz`。

於是：liveness 每 10 秒打一次 `/health` → 連續 3 次 404（`failureThreshold: 3`）→ kubelet 判定容器不健康 → 送 `SIGTERM` 重啟（Exit Code 143）→ 容器重新健康啟動 → 又被同一個錯誤探針砍掉……無限循環。

這是**探針設定錯誤（configuration）**，不是應用故障。順帶一提：readinessProbe 設的是正確的 `/healthz`，所以 readiness 一直過，Pod 始終留在 Service 的 endpoints 裡、流量進得來——但 liveness 仍持續把它砍掉。

## ✅ 修正方式
把 `livenessProbe.httpGet.path` 從 `/health` 改成 `/healthz`，與 readiness 一致：

```yaml
          livenessProbe:
            httpGet:
              path: /healthz          # ← 從 /health 改成 /healthz
              port: 8084
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
```

```bash
kubectl apply -f manifest.yaml
kubectl rollout status deployment/notification-service -n shopnow

# 持續觀察 RESTARTS 應該停止增加（按 Ctrl-C 結束）
watch -n 5 'kubectl get pods -n shopnow -l app=notification-service'
```

修正後 Pod 仍是 `1/1 Running`，但 `RESTARTS` 會停在某個數字不再往上跳，`(xxs ago)` 也不再刷新——代表不再被誤殺。

## 🧠 延伸重點
- **看 Exit Code 判斷死因**：
  - `143`（128+15，SIGTERM）→ 被「優雅地」終止，通常是 liveness 失敗或滾動更新、被 kubelet 主動關掉。
  - `137`（128+9，SIGKILL）→ 被「強制」殺掉，常見於 OOMKilled，或 SIGTERM 後超過 grace period 被補刀。
  - `1` → 程式自己拋例外退出（應用層錯誤，如缺環境變數，見情境 01）。
- **三種 probe 的差別**：
  - `livenessProbe`：失敗就「重啟容器」。本例就是它設錯，把健康的容器一直砍掉。
  - `readinessProbe`：失敗就把 Pod「移出 Service 流量」（不重啟）。本例它設對了，所以流量還進得來。
  - `startupProbe`：給慢啟動的應用一段保護期，期間先不跑 liveness，避免啟動太慢就被誤殺。
- **probe 太敏感也會誤殺健康服務**：`timeoutSeconds` 太短、`failureThreshold` 太小、`initialDelaySeconds` 太短，都可能讓一個正常但偶爾慢一拍的服務被反覆重啟。設定探針時務必確認「路徑正確」且「容忍度合理」。
- 與情境 01 對照：CrashLoopBackOff 是「容器自己崩潰（Exit 1）且 `0/1`」；本例是「容器健康（`1/1 Running`）卻被探針砍（Exit 143）」，看起來很像但死因完全相反。
