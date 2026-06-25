# 解答 — 情境 02：shopnow-frontend 啟動失敗（host port 8080 已被占用）

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `docker compose up -d shopnow-frontend` 失敗，容器停在 `Created`，從未真正 `Up`（見 `status.txt` 的 `docker ps -a`）。
- daemon 直接回報 `port is already allocated`，容器根本沒 start，所以 `docker logs shopnow-frontend` 是空的（沒有任何應用日誌）。

## 🔎 診斷線索（按順序）
1. `status.txt` → `docker ps` 顯示既有容器 `legacy-dashboard` 正 `Up 3 days`，PORTS 欄是 `0.0.0.0:8080->80/tcp`，代表 host 端口 8080 已被它發佈占用。
2. `status.txt` → `docker ps -a` 顯示 `shopnow-frontend` 狀態是 `Created`（不是 `Up`，也不是 `Exited`），表示它連 start 都沒成功。
3. **關鍵在 `logs.txt`**：
   - `Error response from daemon: driver failed programming external connectivity on endpoint shopnow-frontend (...): Bind for 0.0.0.0:8080 failed: port is already allocated`
4. `describe.txt` → `docker inspect legacy-dashboard` 證實它的 `HostConfig.PortBindings` / `NetworkSettings.Ports` 把 host 8080 綁到自己的 container 80；`sudo lsof -i :8080` 顯示是 `docker-proxy` 正在 LISTEN 8080。
5. `events.txt` → `docker events` 看到 `shopnow-frontend` create 之後 `start ... error`、緊接著 `network disconnect`；`ss -ltnp | grep :8080` 同樣指出 8080 被 `docker-proxy`（pid 48190/48197）占用。

## 🎯 根本原因
主機上的 host port **8080 已經被既有容器 `legacy-dashboard` 發佈占用**。`shopnow-frontend` 在 `manifest.yaml` 也要把 host port 8080 對外發佈（`"8080:8080"`），但**同一個 host port 不能同時被兩個容器發佈**，於是 docker 在替新容器設定對外連線（bind 0.0.0.0:8080）時失敗 → `port is already allocated`。這是**主機端口衝突（host port conflict）**，不是映像檔或 nginx 設定的 bug。

## ✅ 修正方式

### 方法一（建議）：把 shopnow-frontend 換一個沒被占用的 host port
保留 legacy-dashboard 不動，把 `manifest.yaml` 的 host 端口改成 8090（container 端口維持不變）：

```yaml
    ports:
      - "8090:8080"   # ← host port 8080 改成 8090，避開衝突
```

```bash
docker compose up -d shopnow-frontend
docker ps                       # shopnow-frontend 應變為 Up，PORTS 顯示 0.0.0.0:8090->8080/tcp
curl -s http://localhost:8090   # 應能取得 nginx 回應
```

### 方法二：若 legacy-dashboard 已無用，停掉它釋放 8080
```bash
docker stop legacy-dashboard     # 釋放 host port 8080
docker compose up -d shopnow-frontend
docker ps                        # shopnow-frontend 應變為 Up，PORTS 顯示 0.0.0.0:8080->8080/tcp
curl -s http://localhost:8080    # 應能取得 nginx 回應
```

> ⚠️ 方法二會讓 legacy-dashboard 對外服務中斷，務必先確認它真的可以下線再執行。

## 🧠 延伸重點
- `ports` 的格式是 `HOST:CONTAINER`。衝突的永遠是**左邊的 host port**（多個容器在 host 上搶同一個對外端口）；右邊的 container port 各自獨立、不會互相衝突。
- 找出「誰占用了某個 port」的常用指令：`sudo lsof -i :8080`、`ss -ltnp | grep :8080`、`docker ps`（看 PORTS 欄）。看到 `docker-proxy` 在 LISTEN，就代表是某個容器發佈了該 host port。
- 同一個 host port 一次只能被一個發佈使用。要讓多個容器都對外，請各自指定**不同的 host port**（例如 8080、8090、8091…），或前面放一個反向代理（nginx / traefik）統一在一個 port 對外、再依路徑分流。
- 與 `case-01` 對照：那個是「容器有 start、但程式自己 exit(1)」；這個是「容器連 start 都失敗、卡在 Created」，所以 `docker logs` 是空的，要看 daemon 的錯誤訊息而不是應用日誌。
