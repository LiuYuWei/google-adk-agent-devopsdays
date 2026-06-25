# 解答 — 情境 04：shopnow-image-processor 處理大圖被 OOM 終止（Exited 137）

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `shopnow-image-processor` 啟動後正常處理了幾張圖，沒幾秒就變成 `Exited (137)`。
- `logs.txt` 的應用日誌**沒有任何 Traceback 或優雅關閉訊息**，跑到一半就斷尾，最後只剩一行 `Killed`。

## 🔎 診斷線索（按順序）
1. `status.txt` → `docker ps -a` 顯示 `STATUS = Exited (137) 15 seconds ago`。Exit Code 137 = 128 + 9（SIGKILL），代表是「被外部訊號砍掉」，不是程式自己 `return 1`。
2. **關鍵在 `describe.txt`**：
   - `docker inspect` 的 `State.OOMKilled: true`、`ExitCode: 137`、`Error: ""`（空字串，不是應用報錯）。
   - `HostConfig.Memory: 268435456` = 256MiB，這就是套在容器上的記憶體上限。
   - 速查指令 `docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}'` → `true 137`。
3. `logs.txt` → 處理到 `Processing batch 3/20`、`Loaded image 7680x4320 ... est=95.0MiB`、`building high-res composite preview` 後**無預警斷尾**，最後一行 `Killed`。被 SIGKILL 的行程沒機會印錯誤或跑 finally，所以日誌看起來像「斷在半路」。
4. `events.txt` → 事件流是 `start → oom → die (exitCode=137)`，明確出現 `oom` 事件。
   - `docker stats` 快照顯示 `MEM USAGE / LIMIT = 254.8MiB / 256MiB`、`MEM % = 99.53%`，記憶體幾乎頂滿。
   - 主機 `dmesg` 出現 `Memory cgroup out of memory: Killed process 23187 (python)` 與 `oom-kill:constraint=CONSTRAINT_MEMCG`，證明是 **cgroup（容器層級）的記憶體上限**被踩爆，不是整台主機沒記憶體。

## 🎯 根本原因
容器被設了 `mem_limit: 256m`（= `--memory=256m`），但這個工作負載要處理 4500x3000 ～ 7680x4320 的大圖、還要在記憶體裡組高解析合成預覽，實際峰值遠超 256MiB。一旦 cgroup 用量達到上限，Linux 核心的 OOM killer 對容器內主行程送出 **SIGKILL**，容器以 `Exited (137)`、`OOMKilled: true` 結束。

屬於**資源配額（記憶體上限）設太低**的問題，不是應用程式 crash、也不是映像檔 bug。

## ✅ 修正方式

### ① 短期：把記憶體上限調高到符合實際需求
把 `manifest.yaml` 的 `mem_limit` 從 `256m` 提高到符合峰值（例如 `1g`，圖更大就 `2g`）：

```yaml
services:
  shopnow-image-processor:
    image: shopnow/shopnow-image-processor:2.3.1
    container_name: shopnow-image-processor
    command: ["python", "-m", "worker.run", "--queue", "image-batches"]
    mem_limit: 1g          # ← 256m 改為 1g（依實測峰值調整）
    environment:
      APP_ENV: "production"
      REDIS_URL: "redis://shopnow-redis:6379/0"
      BATCH_QUEUE: "image-batches"
      LOG_LEVEL: "info"
```

> 如果用的是 `deploy.resources.limits.memory` 寫法，對應改成 `memory: 1G` 即可（概念相同）。

```bash
docker compose up -d                                              # 套用新設定重啟
docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' shopnow-image-processor
# 應為：false 0（不再被 OOM）
docker stats --no-stream shopnow-image-processor                 # 觀察 MEM USAGE 峰值，確認沒貼著 LIMIT
```

### ② 中長期：降低應用本身的記憶體用量
單純加大上限治標不治本，量再大一樣會爆。請從程式面下手：
- **分批 / 串流處理**：一次只載入一張大圖，處理完就釋放，不要把整批圖同時讀進記憶體。
- **及時釋放物件**：處理完的 image / buffer 主動 `close()` / `del`，必要時呼叫 `gc.collect()`，避免記憶體單調成長。
- **避免在記憶體中組超大合成圖**：用 tile / 串流方式輸出，或改用磁碟暫存。
- **設工作併發上限**：worker 同時處理的圖片數量要有上限，跟記憶體預算對齊。

驗證（修完程式後）：

```bash
docker compose up -d
docker stats --no-stream shopnow-image-processor   # 連續跑整批 20 張，MEM % 應穩定在低水位
docker logs shopnow-image-processor                # 應看到完整跑完 20/20、有正常結束訊息，無 Killed
```

## 🧠 延伸重點
- **Exit Code 137 = 128 + 9 (SIGKILL)**：看到 137 就要先懷疑 OOM 或被外部 kill，這是「被外部砍」而非應用自己崩潰。
- **判斷 OOM 的關鍵證據是 `docker inspect` 的 `State.OOMKilled: true`**，搭配 `events` 的 `oom` 事件與主機 `dmesg` 的 `Memory cgroup out of memory`。
- 因為是 SIGKILL，行程沒機會印 stack trace 或跑清理，所以 **logs 常常無預警斷尾**——不要被「日誌看起來正常」誤導。
- docker 的 `--memory` / compose `mem_limit` 與 k8s 的 memory `limits` 是**同一個概念**（都靠 cgroup 限制 + OOM killer 執法）。可與 `kubernetes/case-03` 對照：兩邊根因與判讀方式一致，差別只在查詢工具（`docker inspect` vs `kubectl describe`）。
