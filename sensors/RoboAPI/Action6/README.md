# Action 6（传感器库）

`robots/sensors/RoboAPI/Action6/Action6.usda`

RoboAPI 腕部相机 DJI Osmo Action 6 的可复用模型。挂在库内 Robotiq 2F-85 的 `Sensor=action6` 下，单位姿态相对**夹爪安装面**。

## 变体（都在相机上，不在夹爪 Sensor 选项名上）

| 变体 | 默认 | 可见网格 | 成像（OpenCV 鱼眼，近似） |
| --- | --- | --- | --- |
| `Lens=native` |  | 官方原装镜头保护盖显示，增广镜隐藏 | 官方原生 **155°**，`fx=fy=542.8700`，1280×720，cx=640，cy=360，**k1–k4=0** |
| `Lens=fov_boost` | 是（RoboAPI 配套增广镜） | 原装保护盖隐藏，显示官方装配页的 FOV Boost 镜头网格 | 官网 **182°**；同样因超过 180° 会四角留白，仿真按对角 **179°** 铺满 1280×720（`fx=fy=470.0830`）。其余同上 |
| `ROS=none` | 是 | 无 ROS 发布 | — |
| `ROS=enable` |  | OmniGraph 发布 `/action6/{rgb,camera_info}`（1280×720，无 depth） | — |

增广镜网格来自官网硬件页装配 3D 里的独立零件「极广角镜头 / Ultra-wide lens」（装配查看器按官方 `lensReferences` 的直径 38.65 mm、厚度 17.64 mm 和官方配色生成）。`fov_boost` 显示该网格并隐藏原装保护盖；`native` 相反。

两路 Lens 的仿真相机近裁剪都是 3 cm（刚好越过 FOV Boost 镜头 / 原装保护盖），避免镜头网格挡住画面；viewport 里的外观不受影响。

鱼眼是等距模型由广告 FOV 反推的近似，不是官方标定。颜色来自官方 GLB 的 `baseColorFactor` 与 `COLOR_0`（`action-optics` 没有 factor，用官方顶点色及其均值）。材质在 `/Action6/Looks`（UsdPreviewSurface + OmniPBR）。
