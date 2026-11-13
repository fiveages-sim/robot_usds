# RobotEra STAR1 (FaSim Isaac)

G1-style **2-part** humanoid USD: `Star1_Upper` + `Star1_Lower`, hands via **EE payload**.

| Variant | Default | Notes |
|---------|---------|--------|
| `Upper` | `upper` | pelvis + waist×3 + torso + neck + dual arms (ArtRoot on `base_link`) |
| `Lower` | `none` | `lower` = legs welded on Upper `base_link` (pelvis). **Keeps `floating_base`** so pelvis stays world-fixed for upper-only OCS2 |
| `EE_*` | `none` | `xhand1` → `robots/dexhands/RobotEra/Xhand1` on `*_wrist_roll_link` |
| `Sensor` | `none` | `sensors` = library `d455.usd` on `realsense_link` + optical `head_camera` |
| `Physics` | `physx` | also `physics` / `mujoco` / `none` |
| `ROS` | `none` | `enable` → Upper joint bridge; `fiveages` → in-process `ROS2ControlLaunch` (`robotera_star1` / `full_body` + physics `/clock`) |

**Control contract (important):** `robotera_star1` ros2_control + `fixed_base_tcp` are **upper-only** (waist×3 + arms×14 + neck×2). Leg joints are **not** in HW interfaces / OCS2 — PhysX drives hold leg pose. Do not expect loco WBC with `ROS=fiveages` yet.

**Import policy:** URDF expanded with `type:=none isaac:=true collider:=convex` (no hand meshes, no camera shells). Collision uses visual meshes (convex hull).

## Quick open

```text
robots/humanoid/RobotEra/Star1/env/upper_sorting.usda   # upper + Xhand1 + ROS=fiveages
robots/humanoid/RobotEra/Star1/env/full.usda            # Upper + Lower + Xhand1 + ROS=fiveages
robots/humanoid/RobotEra/Star1/Star1.usda               # asset root
```

Rebuild sources live under `~/star1_isaac_import/` (`prepare_urdf.sh`, `postprocess_part.py`).
