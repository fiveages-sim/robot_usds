# Insta360 Ace Pro 2

`AcePro2.usda`。挂在 Robotiq 2F-85 的 `Sensor=acepro2` 上，姿态相对夹爪安装面。

| 变体 | 默认 | 效果 |
| --- | --- | --- |
| `Lens=native` |  | 保护镜。对角 157°，`fx=fy=535.9545`，1280×720，k1–k4=0 |
| `Lens=ultrawide` | 是 | 极广角镜（直径 46 mm，厚 22 mm）。广告 189°，仿真对角 179°，`fx=fy=470.0830` |
| `Frame=none` |  | 隐藏多功能框 |
| `Frame=utility` | 是 | 显示 `ace-cage`，不改内参 |
| `ROS=none` | 是 | 不发布 |
| `ROS=enable` |  | `/acepro2/{rgb,camera_info}`，1280×720，无 depth |

鱼眼由广告 FOV 等距近似。近裁剪 3 cm。
