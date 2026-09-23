# Wuji Hand2 Sensor=contact_force

PhysX 接触力 → ROS2（MarkerArray / Wrench / Bool）。挂在**手资产**上，与具体臂、机身、stage 解耦。

## 结构

```
payloads/Sensor/
  none.usda | sensors.usda | contact_force.usda + contact_force_publisher.py
Wuji_hand2.usda  Sensor = { none, sensors, contact_force }
Side/right.usda  → tfPrefix=right_hand  topicPrefix=wuji_rh
Side/left.usda   → tfPrefix=left_hand   topicPrefix=wuji_lh
```

## 怎么开

| | 设置 |
|--|--|
| 右手 | `Side=right` + `Sensor=contact_force` |
| 左手 | `Side=left` + `Sensor=contact_force` |
| 关 | `Sensor=none`（默认） |

双臂可同时开：两套 Graph、两套话题（`/wuji_rh/*` 与 `/wuji_lh/*`），互不抢节点名。

## 灵活性（换臂 / 新人形 / 新 stage）

功能跟着 **`Wuji_hand2` prim** 走，不绑定 FiveAges_W2 或某个 env：

1. 任意机械臂 EE 挂载本手资产，并设 `Sensor=contact_force`
2. 或新建空 stage，把 `Wuji_hand2.usda` 拖进来设好 Side/Sensor，PhysX Play
3. handRoot / Graph 路径由脚本从节点 prim **自动发现**（无 `/World/FiveAges_…` 硬编码）
4. RViz：`attachMode=link` 时箭头挂在运控 TF（`right_hand_*` / `left_hand_*`）。若没有 robot_state_publisher，可把 Graph 的 `attachMode` 改成 `world` 看 Isaac 世界坐标

**前提**：仿真引擎为 **PhysX**（ContactSensor）；Newton 下需先切 PhysX。

## 话题

| Side | MarkerArray | TF frame 前缀 |
|------|-------------|---------------|
| right | `/wuji_rh/contact_force_markers` | `right_hand_` |
| left | `/wuji_lh/contact_force_markers` | `left_hand_` |

另有：`contact_wrench/<link>`、`in_contact/<link>`、`any_contact`、`contact_partners`、`contact_hud`。
