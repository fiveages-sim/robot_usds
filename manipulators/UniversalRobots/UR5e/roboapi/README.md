# UR5e RoboAPI 本地配置

配置和标定都放在本目录，不要用 `~/.config/roboapi/`。`config.yaml`、`calibration.json`、`model-api-key` 和 `logs/` 只留在本地，已加入 `.gitignore`，不要提交。

驱动实现见 [roboapi-fasim](https://github.com/fiveages-sim/roboapi-fasim)（也可作为 `lerobot_ros2/submodules/roboapi-fasim`）。

在 ubuntu24 里任意路径执行（先激活环境，并与 Isaac 使用同一个 ROS 域）：

```bash
export ROS_DOMAIN_ID=1
source ~/libraries/lerobot_ros2/.venv/bin/activate
roboapi init -c ~/FaSim-Isaac/robots/manipulators/UniversalRobots/UR5e/roboapi/config.yaml
roboapi http -c ~/FaSim-Isaac/robots/manipulators/UniversalRobots/UR5e/roboapi/config.yaml
```

## 首次 init

1. 先让 Isaac / 运控跑起来（同一 `ROS_DOMAIN_ID`），便于自动探测话题。
2. 向导里臂 / 夹爪 / 相机都选 **FaSim ROS 2**。
3. 若图上能扫到话题，会预填位姿、关节、夹爪和 Image 相机话题（仍可手改）。
4. 单臂 UR5e 一般选 `arm_side=left`。双臂场景会先问 left/right。
5. 相机：`env/fiveages_acepro2.usda` 用 `/acepro2/rgb`；`env/fiveages_action6.usda` 用 `/action6/rgb`。探测到多个 Image 话题时可在列表里选。

标定结果写到同目录的 `calibration.json`。若填写了云端 API Key，还会生成 `model-api-key`；标定本身不需要 Key。

## 启动控制台

`roboapi http` 默认占用 8080。本机 viser 已使用该端口时，在 `config.yaml` 里把 `web.port` 设为 `8081`，控制台开 [http://127.0.0.1:8081/](http://127.0.0.1:8081/)。不要关掉 viser。不要重新执行 `roboapi init`，否则会清掉 `web.port`。

然后打开控制台，到「设置 → 设备 → 坐标标定」。

## 切换控制臂

改 `config.yaml` 中 `arm.arm_side`（`left` / `right`）及对应 `/left_*` 或 `/right_*` 话题与夹爪字段后重启 `roboapi http`。改侧后连接身份变化，通常需要重新标定。

WBC 双臂下进入控制时，会启用当前侧并 `*_ARM_DISABLE` 另一侧，避免对侧仍被跟踪。细节见 roboapi-fasim README。
