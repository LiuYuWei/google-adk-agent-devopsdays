# 解答 — 情境 01：payment-api 一直 CrashLoopBackOff

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `payment-api` 的 2 個 Pod 都是 `0/1`、狀態 `CrashLoopBackOff`，`RESTARTS` 持續累加。
- 容器啟動後 1~2 秒就退出（`describe.txt` 裡 Started 與 Finished 只差約 1 秒）。

## 🔎 診斷線索（按順序）
1. `status.txt` → `CrashLoopBackOff` 且重啟次數一直增加。
2. `describe.txt` → `Last State: Terminated / Reason: Error / Exit Code: 1`，Events 出現 `Back-off restarting failed container`。
3. **關鍵在 `logs.txt`**：因容器已死，要用 `kubectl logs --previous` 看上一輪日誌。
   - 明確寫著：`Required environment variable 'DATABASE_URL' is not set`，pydantic 拋出 `ValidationError ... database_url Field required`。
4. `events.txt` → `kubectl set env --list` 證實 env 清單裡沒有 `DATABASE_URL`；且叢集已有 `payment-db-credentials` Secret。

## 🎯 根本原因
Deployment 的 `env` 區段**漏掉 `DATABASE_URL`**。程式啟動時用 pydantic 驗證設定，必填欄位缺失 → `exit(1)` → kubelet 不斷重啟 → CrashLoopBackOff。屬於**設定（configuration）問題**，不是程式或映像檔 bug。

## ✅ 修正方式
把既有的 `payment-db-credentials` Secret 注入容器：

```yaml
          env:
            - name: APP_ENV
              value: "production"
            - name: REDIS_URL
              value: "redis://redis-master:6379"
            - name: LOG_LEVEL
              value: "info"
            - name: DATABASE_URL          # ← 補上這段
              valueFrom:
                secretKeyRef:
                  name: payment-db-credentials
                  key: DATABASE_URL
```

```bash
kubectl apply -f manifest.yaml
kubectl rollout status deployment/payment-api -n shopnow
kubectl get pods -n shopnow -l app=payment-api   # 應變為 1/1 Running
```

## 🧠 延伸重點
- `CrashLoopBackOff` 是「反覆崩潰、kubelet 退避重啟」的**結果**，真正原因永遠在 `logs --previous`。
- 退避間隔會指數成長（10s→20s→40s…最多 5 分鐘），所以越後面重啟越慢是正常的。
- 與 `case-04` 對照：那個是「容器根本起不來（ConfigError）」，這個是「容器起得來但程式自己崩潰（Exit Code 1）」。
