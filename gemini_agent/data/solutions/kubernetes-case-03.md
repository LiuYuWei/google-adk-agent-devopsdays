# 解答 — 情境 03：recommendation-engine 反覆被 OOMKilled (137)

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `recommendation-engine` 的 Pod 看起來「還活著」：其中一個是 `1/1 Running`，但 `RESTARTS` 已累積到 11、12 次，且最近幾十秒前才又重啟。
- 另一個 Pod 此刻正卡在 `CrashLoopBackOff`。
- 容器啟動正常（Spring Boot 跑得起來），但每隔一兩分鐘就無預警消失再被拉起。

## 🔎 診斷線索（按順序）
1. `status.txt` → 狀態是 `Running` 但 `RESTARTS` 很高（11/12 次）。這種「Running 但一直重啟」就是 OOM 的典型樣貌。
2. **關鍵在 `describe.txt`**：
   - `State: Running`，但 `Last State: Terminated / Reason: OOMKilled / Exit Code: 137`，並有 Started/Finished 時間。
   - `Limits: memory 512Mi`、`Requests: memory 256Mi`、`Restart Count: 11`。
   - Events 只有 `Created`/`Started` 反覆 (x12)，**沒有**獨立的 OOMKilling Warning（cgroup OOM 多半如此，證據在 Last State）。
3. `logs.txt` → 日誌「無預警斷尾」：Tomcat started on port 8082、`Started RecommendationEngineApplication in 8.4 seconds`，處理幾個請求後就斷掉，沒有任何 graceful shutdown。用 `--previous` 看上一輪，斷尾前可看到一行 `java.lang.OutOfMemoryError: Java heap space`。
4. `events.txt` →
   - `kubectl top pod` 顯示記憶體用量已貼著上限（506Mi / 511Mi，逼近 512Mi）。
   - 節點 `dmesg` 撈到核心 OOM Killer 證據：`Memory cgroup out of memory: Killed process 12345 (java)`、`oom-kill:constraint=CONSTRAINT_MEMCG`、`memory: usage 524288kB, limit 524288kB`（524288kB ÷ 1024 = 512Mi）。

## 🎯 根本原因
memory limit 只設 `512Mi`，對這個 **Java 17 + Spring Boot** 服務太低；而 `JAVA_TOOL_OPTIONS: -Xmx480m` 又把 heap 寫死到幾乎吃滿整個 limit，**完全沒留 JVM 堆外空間**（metaspace、thread stacks、GC、堆外 buffer 等）。
結果是：JVM heap + 堆外總和一有負載就超過 512Mi → Linux 核心的 **cgroup OOM Killer 直接送出 SIGKILL** → 容器以 **Exit Code 137** 結束（`Reason: OOMKilled`）→ kubelet 重啟 → 反覆循環。屬於**資源配置（resource sizing）問題**，不是程式或映像檔的功能 bug。

## ✅ 修正方式
重點兩步：① 把記憶體上限調高並留足堆外空間；② 改用「容器感知」的方式設定 heap，不要寫死 `-Xmx`。

```yaml
          env:
            - name: APP_ENV
              value: "production"
            - name: JAVA_TOOL_OPTIONS
              # ← 改用容器感知的百分比，讓 JVM 依 limit 自動換算 heap，並保留堆外空間
              value: "-XX:MaxRAMPercentage=75.0"
            - name: LOG_LEVEL
              value: "info"
          resources:
            requests:
              cpu: 500m
              memory: 768Mi       # ← 調高 request，讓排程器預留足夠記憶體
            limits:
              cpu: 1
              memory: 1Gi         # ← 調高 limit（512Mi → 1Gi），給 JVM 足夠呼吸空間
```

```bash
kubectl apply -f manifest.yaml
kubectl rollout status deployment/recommendation-engine -n shopnow
kubectl get pods -n shopnow -l app=recommendation-engine      # RESTARTS 應停止累加，維持 1/1 Running
kubectl top pod -n shopnow -l app=recommendation-engine       # MEMORY 應穩定在 limit 之下、不再貼頂
```

## 🧠 延伸重點
- **Exit Code 137 = 128 + 9**，9 就是 `SIGKILL`。看到 137 + `Reason: OOMKilled` 就幾乎可以斷定是記憶體被砍。
- **OOMKilled 與 CrashLoopBackOff 的差別**：`OOMKilled` 是「被核心因為記憶體上限而強制砍掉」的**具體死因**；`CrashLoopBackOff` 是「容器反覆崩潰、kubelet 退避重啟」的**統稱結果**。OOM 反覆發生時，Pod 也可能進入 CrashLoopBackOff，但根因仍是記憶體。
- **request vs limit**：`request` 是排程器用來「預留 / 找節點」的保證量，也影響 QoS；`limit` 是「硬上限」，超過 memory limit 就會被 OOMKilled。兩者要一起調，不能只動其中一個。
- **為什麼用 `-XX:MaxRAMPercentage` 而不是 `-Xmx`**：寫死的 `-Xmx` 一旦和 limit 脫鉤就很危險（像本例 480m vs 512Mi 幾乎沒留餘地）；`MaxRAMPercentage` 會讓 JVM 依容器實際的記憶體 limit 自動換算 heap，調整 limit 時 heap 也跟著等比例變動，更安全也更好維護。
