# UR5e RoboAPI 本地配置

配置和标定都放在本目录，不要用 `~/.config/roboapi/`。`config.yaml`、`calibration.json`、`model-api-key` 和 `logs/` 只留在本地，已加入 `.gitignore`，不要提交。

在 ubuntu24 里任意路径执行（先激活环境，并与 Isaac 使用同一个 ROS 域）：

```bash
export ROS_DOMAIN_ID=1
source ~/libraries/lerobot_ros2/.venv/bin/activate
roboapi init -c ~/FaSim-Isaac/robots/manipulators/UniversalRobots/UR5e/roboapi/config.yaml
roboapi http -c ~/FaSim-Isaac/robots/manipulators/UniversalRobots/UR5e/roboapi/config.yaml
```

首次 `init` 会在本目录生成 `config.yaml`。向导里选择三套 `fasim` 组件；相机话题填 `/acepro2/rgb`（若跑的是 `env/fiveages_action6.usda`，则填 `/action6/rgb`）。标定结果写到同目录的 `calibration.json`。

`roboapi init` 若填写了云端 API Key，还会生成 `model-api-key`。标定本身不需要 Key。

`roboapi http` 默认占用 8080。本机 viser 已使用该端口时，在 `config.yaml` 里把 `web.port` 设为 `8081`，控制台开 [http://127.0.0.1:8081/](http://127.0.0.1:8081/)。不要关掉 viser。不要重新执行 `roboapi init`，否则会清掉 `web.port`。

然后打开控制台，到「设置 → 设备 → 坐标标定」。
