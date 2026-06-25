# 解答 — 情境 03：shopnow-report-gen 映像檔 build 一直失敗

> 講師解答卷。學員診斷時請先看 `status.txt`、`describe.txt`、`logs.txt`、`events.txt`。

## 🔔 現象
- `docker build -t shopnow-report-gen:latest .` 跑到一半就中止，最後吐出 `failed to solve ... exit code: 1`。
- `status.txt` 的 `docker images` 裡**根本沒有 `shopnow-report-gen`**，因為映像檔從來沒建成功。
- `docker compose ps` 是空的，沒有任何容器在跑。

## 🔎 診斷線索（按順序）
1. `status.txt` → `docker images` 找不到 `shopnow-report-gen`；`docker compose ps` empty → 連容器都沒有，問題發生在「建置階段」而非「執行階段」。
2. `describe.txt` → `docker image inspect shopnow-report-gen:latest` 回 `Error: No such image`，再次確認映像檔不存在。
3. `logs.txt` → `docker logs shopnow-report-gen` 回 `Error: No such container`。**這是重要的方向判斷**：沒有容器就沒有應用日誌可看，必須回頭去看 build log。
4. **關鍵在 `events.txt`**（build log）：
   - BuildKit 進行到 `[4/5] RUN pip install --no-cache-dir -r requirements.txt` 這層才失敗，前面的 `FROM` / `WORKDIR` / `COPY` 都成功。
   - pip 明確報錯：`ERROR: Could not find a version that satisfies the requirement pandas==99.9.9 (from versions: ..., 2.2.2, 2.2.3)` 與 `ERROR: No matching distribution found for pandas==99.9.9`。
   - 末段附的 `cat requirements.txt` 第 3 行就是 `pandas==99.9.9`——把 build log 的錯誤訊息和這個檔案一比對，根因立刻浮現。

## 🎯 根本原因
`requirements.txt` 把 `pandas` 釘死在**不存在的版本 `99.9.9`**。`pip` 解析相依套件時，從 PyPI 拿到的可用版本最高只到 `2.2.3`，找不到 `99.9.9` → `RUN pip install` 這一層以 `exit code: 1` 失敗 → BuildKit 中止整個 build。屬於**建置期（build-time）的相依設定問題**，不是程式 bug、也不是執行期錯誤。

## ✅ 修正方式
把 `requirements.txt` 改成一個實際存在的版本（build log 顯示最高可用版本是 `2.2.3`）：

```diff
  fastapi==0.111.0
  uvicorn==0.30.1
- pandas==99.9.9
+ pandas==2.2.3
  openpyxl==3.1.5
  python-dateutil==2.9.0
```

重新建置並確認映像檔出現：

```bash
docker build -t shopnow-report-gen:latest .
# 或透過 compose
docker compose build shopnow-report-gen

docker images | grep shopnow-report-gen   # 應該看到 shopnow-report-gen latest
docker compose up -d shopnow-report-gen   # 確認容器能順利啟動
```

## 🧠 延伸重點
- **build-time vs run-time**：這個情境連容器都沒生出來，所以 `docker logs` / `docker compose logs` 一定是空的或回 `No such container`。診斷時要先用 `docker images` 判斷映像檔到底有沒有建成功——沒有就只能看 build log，別再去翻應用日誌。
- **怎麼查可用版本**：用 `pip index versions pandas`（新版 pip）或直接看 build log 裡 pip 列出的 `from versions: ...` 清單；也可以到 PyPI 頁面（pypi.org/project/pandas）確認。
- **避免硬釘錯版本**：與其手寫 `pandas==99.9.9` 這種硬釘，建議用 `pandas>=2.2,<2.3` 這類相容範圍，或用 `pip-compile` / lock 檔（`requirements.lock`、`poetry.lock`、`uv.lock`）鎖定一組「確定存在且互相相容」的版本，CI 才不會踩到打錯字的版本號。
- **怎麼判讀 BuildKit 的錯誤**：`failed to solve: process "/bin/sh -c ..." did not complete successfully: exit code: 1` 代表「某一層的 `RUN` 指令以非 0 結束」。重點是看它前面標的是哪一個 step（這裡是 `[4/5] RUN pip install ...`）以及 `>>>` 指到的 Dockerfile 行號，再往上找該層 stdout/stderr 的真正錯誤訊息（這裡是 pip 的 `No matching distribution found`）。
- 與 `case-01` 對照：那個是「映像檔建好了、容器起得來，但程式啟動時自己 exit 1」；這個是「映像檔根本沒建成功」，兩者排查的起點完全不同。
