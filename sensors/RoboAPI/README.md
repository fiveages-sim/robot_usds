# RoboAPI 腕部相机（传感器库）

- `AcePro2/` — Insta360 Ace Pro 2，变体 `Lens=native|ultrawide`（默认 ultrawide）、`Frame=none|utility`（默认 utility）、`ROS=none|enable`（默认 none）
- `Action6/` — DJI Osmo Action 6，变体 `Lens=native|fov_boost`（默认 fov_boost）、`ROS=none|enable`（默认 none）

切换 `Lens` 会同时改可见附件网格和 OpenCV 鱼眼内参（广告 FOV 的等距近似，k1–k4=0）。`Frame` 只改 Ace Pro 2 多功能扩展框的可见性，不改成像。`ROS=enable` 发布 1280×720 的 `/acepro2|action6/{rgb,camera_info}`（无 depth）。细节见各目录 README。

夹爪支架与 coupling 在 `robots/grippers/Robotiq/2F-85/payloads/Sensor/`（`Sensor=acepro2|action6` 整合套件），不要把支架再放进本目录。

材质写在各相机默认 prim 的 `Looks` 里（UsdPreviewSurface + OmniPBR，颜色只来自官方 GLB），这样被 payload 进场景后绑定仍有效。
