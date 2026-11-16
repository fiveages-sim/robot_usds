# DJI Osmo Action 6

`Action6.usda`。挂在 Robotiq 2F-85 的 `Sensor=action6` 上，姿态相对夹爪安装面。

| 变体 | 默认 | 效果 |
| --- | --- | --- |
| `Lens=native` |  | 保护盖。对角 155°，`fx=fy=542.8700`，1280×720，k1–k4=0 |
| `Lens=fov_boost` | 是 | 增广镜（直径 38.65 mm，厚 17.64 mm）。广告 182°，仿真对角 179°，`fx=fy=470.0830` |
| `ROS=none` | 是 | 不发布 |
| `ROS=enable` |  | `/action6/{rgb,camera_info}`，1280×720，无 depth |

鱼眼由广告 FOV 等距近似。近裁剪 3 cm。
