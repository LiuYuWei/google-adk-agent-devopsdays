# 解答 — 情境 02：order-service 映像檔拉取失敗（ImagePullBackOff）

## 🔔 現象
- 新版 `order-service` Pod 卡在 `ErrImagePull` → `ImagePullBackOff`。
- 舊 ReplicaSet 仍 `Running`，`kubectl rollout status` 最終 `exceeded its progress deadline`（rollout 卡住，但服務沒中斷）。

## 🔎 診斷線索
1. `status.txt` → 新 Pod `ImagePullBackOff`，rollout 逾時。
2. `describe.txt` 的 Events 是關鍵：
   `Failed to pull image "...order-service:1.8.0": ... not found`。
3. `logs.txt` 沒有應用日誌（容器根本沒起來）——提醒學員：ImagePull 類問題不要浪費時間找 logs。
4. `events.txt` 用 `gcloud container images list-tags` 證實 registry **沒有 1.8.0**，最新是 `1.7.3`。

## 🎯 根本原因
Deployment 指定了**不存在的映像檔 tag `1.8.0`**。kubelet 反覆嘗試拉取、失敗、退避，於是 `ImagePullBackOff`。

> 對照其他「拉取失敗」原因（本情境**不是**這些，但講師可一併講解）：
> - `401 Unauthorized` → 私有 registry 缺 `imagePullSecrets`。
> - `connection refused / no such host` → registry 位址錯或網路不通。
> - 本情境是 `not found / manifest unknown` → **tag 不存在**。

## ✅ 修正方式
把 tag 改成存在的版本（`1.7.3`）：

```bash
# 方法 A：直接改 image
kubectl set image deployment/order-service \
  order-service=gcr.io/shopnow-prod/order-service:1.7.3 -n shopnow

# 方法 B：改 manifest.yaml 後重新套用
#   image: gcr.io/shopnow-prod/order-service:1.7.3
kubectl apply -f manifest.yaml

kubectl rollout status deployment/order-service -n shopnow   # 應順利完成
```

## 🧠 延伸重點
- 正式環境避免用 `latest`：無法回溯、難重現；但也別亂指定不存在的明確 tag。
- 因為設了 `maxUnavailable: 0`，舊 Pod 在新 Pod 健康前不會被砍掉，所以**使用者其實沒感受到中斷**——這是滾動更新的保護機制。
