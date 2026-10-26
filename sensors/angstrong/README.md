# Angstrong Nuwa-XB40

- Asset: `nuwa-xb40.usd`（材质在 USD `/World/Looks`）
- Stage: meters, upAxis=Z（sensor-local: +Z 朝前窗，+X 沿壳体；与 URDF/GLB 一致）
- Used by: G1-D / G1D_Chassis `chassis_left_camera` / `chassis_right_camera`

## Optical Camera

G1D 上 Isaac `Camera` 使用的内参（与库内 D435 / Isaac 默认镜头同量级）：

| Param | Value |
|-------|-------|
| focalLength | 18.147562 |
| horizontalAperture | 20.955 |
| verticalAperture | 15.716 |
| clippingRange | (0.01, 1e7) |

见 `G1D` / `G1D_Chassis` `payloads/Sensor/sensors.usda`。

## L/R 命名（GLB）

GLB `"right camera"` = 机器人 **+Y（左）**；`"left camera"` = **−Y**。挂载只按 URDF TF / link 名。
