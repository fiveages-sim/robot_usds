# RobotEra Xbot-L (FaSim Isaac)

G1-style **2-part** humanoid USD: `XbotL_Upper` + `XbotL_Lower`, hands via **EE payload**.

| Variant | Default | Notes |
|---------|---------|--------|
| `Upper` | `upper` | waist + torso + neck + dual arms (ArtRoot) |
| `Lower` | `none` | `lower` = legs FixedJoint on `waist_roll_link`; releases Upper `floating_base` (full robot free-floating). `none` keeps upper world-fixed for sorting |
| `EE_*` | `none` | `xhand1` → `robots/dexhands/RobotEra/Xhand1` |
| `Sensor` | `none` | `sensors` mounts library `d455.usd` (from `sensor_models` d455.glb) on empty `realsense_link` |
| `Physics` | `physx` | also `physics` / `mujoco` / `none` |
| `ROS` | `none` | `enable` → Upper `/isaac/joint_states`+`/joint_command` bridge; `fiveages` → in-process `ROS2ControlLaunch` (`robotera_xbotl` / `full_body` + physics `/clock`, no JointState bridge) |

**Import policy:** URDF expanded with `type:=none isaac:=true` (no hand meshes, no camera shells). Collision uses visual meshes (convex hull), not simplified boxes.

## Quick open

```text
robots/humanoid/RobotEra/XbotL/env/upper_sorting.usda   # parcel sorting (upper only + Xhand1)
robots/humanoid/RobotEra/XbotL/env/full.usda            # Upper + Lower + Xhand1
robots/humanoid/RobotEra/XbotL/XbotL.usda               # asset root
```

Rebuild sources live under `~/xbotl_isaac_import/` (`prepare_urdf.sh`, `postprocess_part.py`).
