# UR5e (FaSim Isaac wrapper)

FaSim 包装官方 Isaac Sim 6.2 UR5e / Robotiq 2F-85 资产。网格和运动学仍留在官方资产区，本目录只放引用脚本、EE payload 和 fiveages 运控图。

资产根由 `mount_asset_root.py` 在打开 stage 时通过 `get_assets_root_path()` 解析（遵循 `ISAACSIM_ASSET_REGION_PROFILE` / `ISAACSIM_ASSET_ROOT`）。本机 `config/fa_sim.local.conf` 已设 `RUN_ASSET_REGION_PROFILE="china"`。不要在 USDA 里写死 S3 / omniverse-content URL。

首次在 Isaac GUI 打开带 `OmniScriptingAPI` 的 stage 时，需要允许执行 USD 内的 Python BehaviorScript（与 warehouse env 相同）。可用 `/app/scripting/ignoreWarningDialog=true` 跳过确认。

## 官方相对路径

- 手臂：`Isaac/Robots_Multiphysics/UniversalRobots/ur5e/ur5e.usda`
- 夹爪：`Isaac/Robots_Multiphysics/Robotiq/2F-85/Robotiq_2F_85.usda`

经典路径 `Isaac/Robots/UniversalRobots/ur5e/ur5e.usd` 与 `Isaac/Robots/Robotiq/2F-85/Robotiq_2F_85_edit.usd` 在国内 CDN 上同样存在；本包装用 Multiphy 版本，因其自带 Physics / Mimic 变体。官方资产里没有 UR7e。UR5 CB3（`Isaac/Robots/UniversalRobots/ur5/ur5.usd`）未封装。

官方 Multiphy UR5e 有 `flange` / `ft_frame`，没有 `tool0`。本包装在 `wrist_3_link/flange` 下补了官方 ROS-Industrial `tool0`（相对 flange 为 `rpy(pi/2, 0, pi/2)`，相对 `wrist_3_link` 为单位姿）。夹爪挂在 `tool0` 上、伸出沿 +Z，并绕 tool0 Z 转 `π/2`，把官方 Multiphy 2F-85 沿 Y 的张口对齐到 tool0 的 X（RoboAPI：指尖连线平行于 `X_EE`；ROS `robotiq_gripper_description` 2F85 也是沿 X）。库资产本身仍保持官方 Y 向坐标系，不要去改。不要启用官方 `Gripper=robotiq_2f_85`：那条固定关节是按 flange 约定写的，会把接近方向也转歪。

## 变体

| 集合 | 选项 | 默认 |
| --- | --- | --- |
| Physics | 官方 `none` / `physics` / `physx` / `mujoco` | `physx` |
| ROS | `none` / `fiveages` | 机器人文件为 `none`；`env/fiveages.usda` 为 `fiveages` |
| EE | `none` / `robotiq85` | 机器人文件为 `none`；`env/fiveages.usda` 为 `robotiq85` |
| Sensor | 官方 `none` / `sensors` | `none` |
| Robot | `none` | `none` |
| Gripper（官方） | 保持 `none` | `none` |

没有单独的 `Physics=newton` 变体，这与当前分支上 CR5 等手臂一致。Newton 是 `./run.sh --physics newton` 的仿真后端；stage 根上的 `PhysicsScene` 带 `NewtonSceneAPI` + `PhysxSceneAPI`。

六轴 PhysX Drive 在包装层写成 FiveAges 常用值（与 CR5 / Piper 相同）：`stiffness=60000`、`damping=6000`、`maxForce=100`、`type=force`。官方 Multiphy 默认近端阻尼过小，跟轨迹时容易发飘/发涩。

`root_joint` 上补齐 `PhysxArticulationAPI`（与 CR5 一致）：`enabledSelfCollisions=0`、`solverPositionIterationCount=64`、`solverVelocityIterationCount=4`、`sleepThreshold=5e-5`、`stabilizationThreshold=1e-5`。六轴另加 `PhysxJointAPI`，`maxJointVelocity=180`（deg/s，UR5e 额定）。

官方夹爪主关节 prim 名是 `finger_joint`。FaSim 夹爪库用 `payloads/Joints/ros2_names.usda`（Dex1 Side 同款：停用官方关节并写出新 prim）把 DOF 对齐到描述包：`gripper_joint`、`left_inner_knuckle_joint`、`right_inner_knuckle_joint`，以便 `IsaacSimSystem` 与 ros2_control HW 一致。

`EE=robotiq85` 引用夹爪库 `robots/grippers/Robotiq/2F-85/Robotiq_2F_85.usda`（和 CR5 引用 `grippers/ChangingTek/AG2F90` 同一方式），再由库里的 `mount_asset_root.py` 挂上官方 Multiphy 2F-85。不要从 Content Browser 单独打开或拖入官方 `Robotiq_2F_85_edit.usd`，那样夹爪不会挂到 `tool0` 上。打开机器人文件后再改 EE 变体时，若夹爪还没出现，重新加载 stage；`env/fiveages.usda` 已默认 `EE=robotiq85`。

## 打开 / 启动

在 FaSim-Isaac 里打开：

```bash
./run.sh --physics newton --asset-region china
```

然后加载：

`robots/manipulators/UniversalRobots/UR5e/env/fiveages.usda`

或只打开机器人资产：

`robots/manipulators/UniversalRobots/UR5e/UR5e.usda`

进程内 fiveages 运控（`hardware:=isaac_sim`）由 USD 里的 `ROS2ControlLaunch` 拉起，`inputs:robot=ur5e`，`type` 从 EE 变体读取。也可以在已 source 的工作空间里单独启动：

```bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=ur5e type:=robotiq85 hardware:=isaac_sim isaac_prim_path:=/World/UR5e/root_joint
```

Topic-based 驱动用 `hardware:=isaac`。`ocs2_arm_controller` 默认 robot 是 `cr5`，UR5e 必须显式传入 `robot:=ur5e`。

## RoboAPI 腕部相机

夹爪-only 场景仍是 `env/fiveages.usda`（`EE=robotiq85`，`Sensor` 保持默认 `none`）。

带腕部相机的场景：

- `env/fiveages_acepro2.usda` — 光学桌 **fruits** 场景 + `Sensor=acepro2`（`Lens=ultrawide`、`Frame=utility`、`ROS=enable` → `/acepro2/{rgb,camera_info}`）。UR5e 基座位姿与 CR5 `env/fruits.usda` 一致（`(-0.4, 0, 0.8)`，朝向桌面）；关节初始为 `ocs2` / `ros2_controllers` 的 **home_1**（RoboAPI Home）。场景 `global_camera` 与其 ROS 图已关闭，只用腕部相机。`ROS2ControlLaunch.inputs:infoFile=flange` → `ur5e_description/config/ocs2/flange.info`（`eeFrame=flange`）。
- `env/fiveages_action6.usda` — 同上 fruits 场景，`Sensor=action6`（`Lens=fov_boost`、`ROS=enable` → `/action6/{rgb,camera_info}`），同样 `infoFile=flange`。

未点 Play 时，仅写 `state:angular:physics:position` **不会**把连杆画到目标角（Isaac 要等物理或 FK teleport）。这两个 env 在 UR5e 上设了 `customData:fasim_initial_joint_pose=home_1`，由 `mount_asset_root.py` 在挂载后调用 `isaacsim.robot.poser.apply_joint_state` 做编辑态 teleport；Stop 后也会再应用一次。请允许 BehaviorScript，并确认 kit 里有 `isaacsim.robot.poser`（`isaacsim.exp.full` 默认带）。

`payloads/EE/robotiq85_acepro2.usda` 与 `robotiq85_action6.usda` 是可选薄包装；默认入口仍是上面两个 env（`UR5e.usda` 未改，没有新增 EE 变体）。

## RoboAPI 本地配置

设备配置和标定文件放在 [`roboapi/`](roboapi/)，由 `roboapi init` 在本地生成（`config.yaml`、`calibration.json`，以及可选的 `model-api-key`）。这些文件和运行日志不要提交到 git，也不要写到 `~/.config/roboapi/`。启动命令见该目录的 README。

