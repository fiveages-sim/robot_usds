# Slamtec G1D_Chassis

Unitree G1-D 用的 **Slamtec 差速底盘** USD（`Slamtec/` 仅为供应商目录）。

- 入口：`G1D_Chassis.usda`
- Variants：`Physics` / `ROS` / `Sensor` / `Robot`（与整机同名约定）
- ROS=`enable`：官方 DiffDrive ← `/cmd_vel`，`/odom`；左右轮同向
- Sensor=`sensors`：Nuwa×2、超声×2、RPLIDAR S2
- PhysX：支撑轮球底相对驱动轮接地面 **−0.6 mm**

被 `humanoid/Unitree/G1D` 的 `Chassis=chassis` 引用。勿把底盘埋进 G1D `components/`。
