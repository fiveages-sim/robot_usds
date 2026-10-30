# Unitree G1-D (FaSim-Isaac)

宇树 **G1-D** 轮式双臂人形仿真资产。入口 `G1D.usda`；底盘在
`robots/mobile_base/Slamtec/G1D_Chassis/`；末端在通用库。

源 description：`unitree_g1d_description`（ROS2）。

## 路径

| 路径 | 说明 |
|------|------|
| `G1D.usda` | 整机入口 |
| `env/empty.usda` | 空场景 + 默认变体 |
| `payloads/` | Physics / ROS / Sensor / 部件 / EE |
| `components/` | `G1D_Lift`（底盘在 Slamtec；躯干/头/双臂在 `../G1/components/`） |
| `../G1/components/` | 共享 `G1_Body`、`G1_Arms` |
| `../../../../mobile_base/Slamtec/G1D_Chassis/` | Slamtec 差速底盘（共享） |
| `../../../../grippers/Unitree/{Dex1,RubberHand}/` | Dex1 平行夹爪、橡胶手 |
| `../../../../dexhands/Unitree/Dex3/` | Dex3 |
| `../../../../dexhands/BrainCo/Revo2/` | Revo2（复用） |

## Variants

根层 `prepend variantSets`：`Physics`, `ROS`, `Sensor`, `Chassis`, `Lift`, `BodyHead`, `Arms`, `EE_Left`, `EE_Right`；`Robot` 最后。

| Variant | 取值 | 说明 |
|---------|------|------|
| Physics | `none` / `physics` / **`physx`** / `mujoco` | 默认 physx |
| ROS | `none` / **`enable`** | DiffDrive + joint + odom 图 |
| Sensor | **`none`** / `sensors` | 底盘 Nuwa×2、超声×2、RPLIDAR 外壳 + `G1_Body` `d435_link/head_camera`（仅光学 Camera）；腕部相机在 Dex1 `Sensor=camera` |
| Chassis | `None` / `chassis` | 引用 Slamtec `G1D_Chassis` |
| Lift | `None` / `lift` | 立柱；`LZ_mt`/`LZ_it` **各自 PD**（非 mimic） |
| BodyHead | `None` / `bodyhead` | 躯干+头（G1 无头关节，合一块） |
| Arms | `None` / `arms` | 引用 `G1/components/G1_Arms`（左右链同资产） |
| EE_Left / EE_Right | **`none`** / `rubber_hand` / `revo2` / `dex3` / `dex1` | 挂在 `*_tcp` |
| Robot | **`none`** / `robot` | 运控图等（默认 none） |

**Dex1 自身**另有 `Sensor=none|camera`（腕部外壳+Camera）。G1D `EE=dex1` 默认把子资产设为 `Sensor=camera`。

推荐整机：`Chassis/Lift/BodyHead/Arms=chassis|lift|bodyhead|arms`，`ROS=enable`，按需 `Sensor`/`EE`。资产根默认 `Physics=physx`（否则无 ArtRoot，双臂会从肩散架）；**env/mount 不要 sticky Physics**，子件由父 `payloads/Physics/*` push。Newton 时改选 `mujoco` / Reload。`Arms=arms` 需同时 `BodyHead=bodyhead`。

## ROS 话题（`ROS=enable`）

| 话题 | 方向 | 说明 |
|------|------|------|
| `/cmd_vel` | sub | DiffDrive → 左右驱动轮 |
| `/odom` | pub | 里程计 |
| `/isaac/joint_states` | pub | `nodeNamespace=isaac` + `/joint_states` |
| `/isaac/joint_command` | sub | 升降/腰等位置（`LZ_mt_Joint`、`LZ_it_Joint`、`waist_pitch_joint`、`waist_yaw_joint` 等） |

TF：`odom` → 底盘（odom-only，无 map）。

## 空场景

```text
env/empty.usda
```

打开后默认：整机部件开、`EE=none`、`Sensor=sensors`、`ROS=enable`；`Physics` 跟当前仿真引擎（无 authored 默认），地面用 `environment/.../Grid/default_environment.usd`。

## 相关

- Description：`~/ros2_ws/src/robot-descriptions/humanoid/Unitree/unitree_g1d_description`
- Skills：`fasim-urdf-isaac-import`、`fasim-dexhand-asset`
