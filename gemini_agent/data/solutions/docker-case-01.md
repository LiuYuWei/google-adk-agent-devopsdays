# 解答 — 情境 01：shopnow-api 容器啟動即退出（Exited (1)）

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `docker compose ps` 顯示 `shopnow-api` 的 STATUS 是 `Exited (1) 8 seconds ago`，容器一啟動就掛掉。
- 相依的 `shopnow-redis` 一切正常（`Up ... (healthy)`），所以問題出在 api 容器本身，不是 redis。
- 容器幾乎是「秒退」：`describe.txt` 裡 `StartedAt` 與 `FinishedAt` 只差不到 1 秒。

## 🔎 診斷線索（按順序）
1. `status.txt` → `shopnow-api` 是 `Exited (1)`，`shopnow-redis` 是 `Up`。退出碼 1 代表「應用程式自己決定結束」，不是被外力殺掉。
2. `describe.txt` →
   - `State.Status = "exited"`、`Running = false`、`ExitCode = 1`。
   - `OOMKilled = false`、`Error = ""`：排除記憶體不足（137）與 daemon 層級錯誤，問題在應用程式內部。
   - `RestartCount = 0`：compose 設了 `restart: "no"`，所以不會像 k8s 一樣反覆重啟。
   - `Config.Env` 列出了 `APP_ENV`、`REDIS_URL`、`LOG_LEVEL`、`PORT`，**就是沒有 `JWT_SECRET`**。
   - 補充指令 `docker inspect --format '{{.State.ExitCode}}' shopnow-api` 直接回 `1`。
3. **關鍵在 `logs.txt`**：用 `docker logs shopnow-api` 看應用層輸出。
   - 啟動到 `validating required runtime settings` 後就拋出 Python Traceback。
   - 最後一行寫得很清楚：`RuntimeError: Environment variable 'JWT_SECRET' is required but not set`。
4. `events.txt` → 事件流是 `create → start → die`，`die` 那行帶 `exitCode=1`。確認容器是「啟動後立刻自己死掉」，不是根本沒起來。

## 🎯 根本原因
應用程式在啟動時會檢查必填環境變數 `JWT_SECRET`（用來簽發 / 驗證 JWT token），偵測不到就 `raise RuntimeError` 並以 `exit(1)` 結束。

而 `docker-compose.yaml` 的 `environment` 區段**漏掉了 `JWT_SECRET`**，所以容器一啟動就退出。這是**設定（configuration）問題**，不是程式 bug 或映像檔損壞。

## ✅ 修正方式
在 `manifest.yaml`（docker-compose.yaml）的 `environment` 補上 `JWT_SECRET`：

```yaml
    environment:
      APP_ENV: "production"
      REDIS_URL: "redis://shopnow-redis:6379/0"
      LOG_LEVEL: "info"
      PORT: "8000"
      JWT_SECRET: "${JWT_SECRET}"        # ← 補上這行，由 .env 注入，勿寫死
```

搭配 `.env` 檔（不要 commit 進版控）：

```dotenv
JWT_SECRET=請改成夠長的隨機字串_例如用 openssl rand -hex 32 產生
```

重新啟動並確認：

```bash
docker compose up -d
docker compose ps          # shopnow-api 應變為 Up
docker logs shopnow-api    # 應看到正常啟動、uvicorn 開始監聽 8000
```

> 臨時驗證也可以直接帶環境變數：`docker run -e JWT_SECRET=... shopnow/shopnow-api:1.6.0`，但正式環境請走 `.env` 或 secret manager。

## 🧠 延伸重點
- **看懂退出碼**：`Exit (1)` = 應用層自己回傳非 0、主動退出（多半是程式邏輯 / 設定錯誤）；對比 `137` 是被 OOM Killer 殺掉（SIGKILL，記憶體爆掉，見 `docker/case-04`）、`143` 是收到 SIGTERM 被優雅終止。
- **崩潰原因永遠先看 `docker logs`**：`docker compose ps` 只告訴你「死了」，`docker inspect` 告訴你「怎麼死的（exit code / OOM）」，真正的「為什麼」要靠應用程式日誌。
- **密鑰不要寫死在 compose 或映像檔裡**：`JWT_SECRET` 這類敏感值應放 `.env`（加進 `.gitignore`）或 secret manager，並在程式啟動時做必填檢查（fail fast），讓設定錯誤在啟動瞬間就被發現，而不是上線後才出包。
