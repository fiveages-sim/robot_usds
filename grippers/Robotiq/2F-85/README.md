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

## Sensor

本地变体，默认 `none`。`acepro2` / `action6` 是整合套件（支架 + coupling + 相机），不再单独配对 `Bracket`。

| 变体 | 作用 |
| --- | --- |
| `Sensor=none` | 无支架/相机；库内夹爪保持官方姿态（手臂安装偏航由引用方的 EE payload 写）。 |
| `Sensor=acepro2\|action6` | 官方 RoboAPI 腕部支架与螺丝、法兰↔夹爪官方转接环 `coupling`（白/银色环 + 黑色通信线与接头）、以及 `robots/sensors/RoboAPI/{AcePro2,Action6}`。相对夹爪安装面。同时把夹爪沿 tool0 Z 平移 **0.007598894 m**（7.5989 mm）——官方 assembly 量到的法兰→夹爪面联轴节厚度，两套相机相同。官方 UR 腕部和官方夹爪本体/手指不再加入，以免和 Isaac UR5e、库内 2F-85 重复。颜色来自官方 GLB 的 `COLOR_0`。增广镜 / 极广角是**相机自己的** `Lens`（以及 Ace 的 `Frame`）变体，不在 Sensor 选项名上。 |

当前 UR5e `payloads/EE/robotiq85.usda` 把 EE 的姿态和 `AssemblerFixedJoint` 写成绕 tool0 Z 的 `π/2`（平移为 0）。带相机的场景（`env/fiveages_acepro2.usda`、`env/fiveages_action6.usda`）会在 EE 上再写同一偏航，并沿 tool0 Z 加上 7.5989 mm 联轴节偏移，保证关节与 xform 一致。

第一次打开带 BehaviorScript 的 stage 时，若弹出允许 USD Python 的提示，需要允许；或用 `/app/scripting/ignoreWarningDialog=true`。
