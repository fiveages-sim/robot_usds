# Ace Pro 2（传感器库）

`robots/sensors/RoboAPI/AcePro2/AcePro2.usda`

RoboAPI 腕部相机 Insta360 Ace Pro 2 的可复用模型。挂在库内 Robotiq 2F-85 的 `Sensor=acepro2` 下，单位姿态相对**夹爪安装面**（不是 UR 法兰）。支架与 coupling 也在该 Sensor payload 里，不在本文件。

## 变体（都在相机上，不在夹爪 Sensor 选项名上）

| 变体 | 默认 | 可见网格 | 成像（OpenCV 鱼眼，近似） |
| --- | --- | --- | --- |
| `Lens=native` |  | 官方原装保护镜（lens guard）显示，极广角镜头隐藏 | 官方标准镜头 **157°** 对角，`fx=fy=535.9545`，1280×720，cx=640，cy=360，**k1–k4=0** |
| `Lens=ultrawide` | 是（RoboAPI 推荐：极广角镜头） | 原装保护镜隐藏，显示官方装配页的极广角镜头网格 | 官网光学设计上限 **189°**；Isaac 无法对超过 180° 的光线成像，仿真按对角 **179°** 铺满 1280×720（`fx=fy=470.0830`），避免四角留白。其余同上 |
| `Frame=none` |  | 多功能扩展框隐藏 | 不改内参 |
| `Frame=utility` | 是（RoboAPI 推荐：Utility Frame） | 官方重建外观中的 `ace-cage` prim | 不改内参 |
| `ROS=none` | 是 | 无 ROS 发布 | — |
| `ROS=enable` |  | OmniGraph 发布 `/acepro2/{rgb,camera_info}`（1280×720，无 depth） | — |

极广角镜头网格来自官网硬件页装配 3D 里的独立零件「极广角镜头 / Ultra-wide lens」（装配查看器按官方 `lensReferences` 的直径 46 mm、厚度 22 mm 和官方配色生成）。`ultrawide` 显示该网格并隐藏原装保护镜；`native` 相反。

两路 Lens 的仿真相机近裁剪都是 3 cm（刚好越过极广角镜头 / 原装保护镜），避免镜头网格挡住画面；viewport 里的外观不受影响。

鱼眼是等距模型由广告 FOV 反推的近似，不是官方标定。RoboAPI USB 画面为 MJPG 1280×720 @ 30 FPS。

颜色来自官方 GLB 的 `baseColorFactor`（相机零件）和 `COLOR_0`（若有），没有自造色板。官方模型不含产品贴图。材质在 `/AcePro2/Looks`（UsdPreviewSurface + OmniPBR），打开整机场景时才能跟着 payload 一起进来。
