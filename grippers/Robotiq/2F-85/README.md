# Robotiq 2F-85

FaSim 夹爪库里的 Robotiq 2F-85 包装，引用官方 Isaac 6.2 Multiphy 资产（中国区根路径由 `mount_asset_root.py` 解析），不把官方夹爪网格拷进仓库。

路径：`robots/grippers/Robotiq/2F-85/Robotiq_2F_85.usda`

相对官方资产：`Isaac/Robots_Multiphysics/Robotiq/2F-85/Robotiq_2F_85.usda`

机械臂按 CR5 的方式在 EE payload 里引用这个文件。UR5e 的变体名是 `robotiq85`，挂在 `tool0` 上（Z 朝外）。手臂 EE payload 绕 tool0 Z 转 `π/2`，把本库沿 Y 张开的手指对齐到 tool0 X（RoboAPI / ROS 2F85）。本库默认 prim 保持官方坐标系，不要在这里转。不要打开官方 UR5e 的 `Gripper` 变体，它是沿 `flange` 安装的，会把接近方向转歪。

## 关节命名（对齐 ros2_ws）

官方 Multiphy 主关节是 `finger_joint`，描述包 / AdaptiveGripper 用 `gripper_joint`。`IsaacSimSystem` 按 USD **prim 名**匹配 DOF，因此本包装用 subLayer `payloads/Joints/ros2_names.usda`（与 Dex1 Side 相同：停用官方关节并写出新 prim）：

| 官方 prim | FaSim / ros2_ws prim |
| --- | --- |
| `finger_joint` | `gripper_joint` |
| `left_inner_finger_knuckle_joint` | `left_inner_knuckle_joint` |
| `right_inner_finger_knuckle_joint` | `right_inner_knuckle_joint` |

其余（`right_outer_knuckle_joint`、`left/right_inner_finger_joint`）名称已一致。PhysX mimic 的 `referenceJoint` 已改指 `gripper_joint`。

## Side（双臂）

本地变体，默认 `default`。M6 / W2 等双臂主机在 EE 挂载上 sticky `Side=left|right`（与 AG2F90 / Dex1 相同）：

| Side | 主 DOF | 腕部光学 Camera（Sensor=acepro2\|action6） |
| --- | --- | --- |
| `default` | `gripper_joint` | `wrist_camera/optical_frame/Camera` |
| `left` | `left_gripper_joint` 等 `left_*` 前缀 | `left_hand_camera` |
| `right` | `right_gripper_joint` 等 `right_*` 前缀 | `right_hand_camera` |

手指解剖名里的 left/right（如 `left_inner_knuckle_joint`）在 Side=left 下会变成 `left_left_inner_knuckle_joint`，与臂 Side 前缀叠加，避免双臂 DOF 撞名。Side 相机重命名会烘焙 AcePro2 ultrawide 成像参数；单臂 UR5e/CR5 保持 `Side=default`，Lens 变体仍作用在 `Camera` 上。

## Sensor

本地变体，默认 `none`。`acepro2` / `action6` 是整合套件（支架 + coupling + 相机），不再单独配对 `Bracket`。

| 变体 | 作用 |
| --- | --- |
| `Sensor=none` | 无支架/相机；库内夹爪保持官方姿态（手臂安装偏航由引用方的 EE payload 写）。 |
| `Sensor=acepro2\|action6` | 官方 RoboAPI 腕部支架与螺丝、法兰↔夹爪官方转接环 `coupling`（白/银色环 + 黑色通信线与接头）、以及 `robots/sensors/action_camera/{Insta360/AcePro2,DJI/Action6}`。相对夹爪安装面。同时把夹爪沿工具 Z 外移 **0.00745 m**。支架、转接环和相机再沿夹爪 Z 退回 **0.0032 m**，相对法兰保持原位。不带相机时不外移。两套相机相同。官方 UR 腕部和官方夹爪本体/手指不再加入，以免和 Isaac UR5e、库内 2F-85 重复。颜色来自官方 GLB 的 `COLOR_0`。增广镜 / 极广角是**相机自己的** `Lens`（以及 Ace 的 `Frame`）变体，不在 Sensor 选项名上。 |

当前 UR5e `payloads/EE/robotiq85.usda` 只写绕 tool0 Z 的 `π/2`，不钉平移。`Sensor=acepro2|action6` 沿工具 Z 外移 7.45 mm；带相机的场景会再写同一偏航和这段平移，保证关节与 xform 一致。支架、转接环和相机相对夹爪退回 3.2 mm。

第一次打开带 BehaviorScript 的 stage 时，若弹出允许 USD Python 的提示，需要允许；或用 `/app/scripting/ignoreWarningDialog=true`。
