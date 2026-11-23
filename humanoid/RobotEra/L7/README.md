# RobotEra L7 — Phase 1

入口：`L7.usda`，默认 prim `/L7`。默认 Upper=upper、Lower=none、EE_Left=none、EE_Right=none、Physics=physx、Robot=none、ROS=none、Sensor=none。当前仅提供这些选项；Lower 和 XHand1 不可选择，ROS/Sensor 预留接口。

根层参考 `payloads/base.usda`，各 Variant 以 payload 组合。Upper 引用现有组件 `components/L7_Upper/L7_Upper.usda`，Physics 选择组件的 physx variant。组件的 base 以 sublayer 加载 robot.usda，并通过 instances.usda 引用 geometries.usd；其 physx.usda 以 sublayer 加载 physics.usda。所有新增引用使用相对路径。

L7 组件未指定默认 Physics；通过入口打开时明确选择 physx。其固定基座和 ArticulationRoot 在组件的 root_joint 上，目标为 base；与 Star1 的 base_link ArticulationRoot 结构不同。不要复制 Star1 Lower 的 root_joint 停用或固定关节参数。

Phase 2：建立独立 L7 Lower，核对原始模型骨盆连接、坐标系、质量惯量和关节；在组合层连接上下身并保证唯一 articulation root 与目标固定/浮动基座策略，进行 PhysX 拓扑、自由度、碰撞及步进验证。

Phase 3：审计 L7 左右腕法兰和 Xhand1 Side、Flange、root_joint，按 L7 真实安装参数建立独立 EE payload，处理嵌套 articulation root，分别验证左右及双手组合的坐标、关节、碰撞与物理步进。
