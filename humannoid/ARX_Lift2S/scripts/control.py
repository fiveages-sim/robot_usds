import numpy as np
import omni.graph.core as og

def setup(db: og.Database):
    pass

def cleanup(db: og.Database):
    pass

def compute(db: og.Database):
    # 速度缩放系数 (根据电机转速和轮径调整，通常 rad/s 为单位)
    # 若 Isaac Sim 中驱动增益(Gain)较小，可增大此值
    vel_scale = 1.0

    # 获取输入指令
    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega = db.inputs.Desired_Angular_Velocity

    # 1. 轮子位置 (从 URDF 的 <joint> <origin> 标签中提取)
    # wheel1: xyz="0.15361 0.29246 -0.093"
    # wheel2: xyz="0.15361 -0.29245 -0.093"
    # wheel3: xyz="-0.35293 0 -0.093"
    wheel_positions = np.array([
        [0.15361, 0.29246],   # wheel 1
        [0.15361, -0.29245],  # wheel 2
        [-0.35293, 0.0]        # wheel 3
    ])

    # 2. 轮子滚动方向角 (Theta)
    # 在全向轮结构中，滚动方向通常垂直于关节轴心。
    # URDF 中 wheel1_joint 的 rpy="0 0 1.0472" (60度)
    # 滚动方向 theta = 关节偏航角 + 90度 (PI/2)
    PI = np.pi
    wheel_joint_yaws = np.array([1.0472, -1.0472, 0.0]) # 对应 60, -60, 0 度
    wheel_angles = wheel_joint_yaws + PI/2

    vel_cmd = np.zeros(3)

    for i in range(3):
        x_i, y_i = wheel_positions[i]
        theta_i = wheel_angles[i]

        # 线性速度分量：将机器人的 vx, vy 投影到轮子的滚动方向上
        linear_component = vx * np.cos(theta_i) + vy * np.sin(theta_i)

        # 角速度分量：v = omega * r，投影到滚动方向
        # 公式：omega * (x_i * sin(theta_i) - y_i * cos(theta_i))
        angular_component = omega * (x_i * np.sin(theta_i) - y_i * np.cos(theta_i))

        vel_cmd[i] = (linear_component + angular_component) * vel_scale

    # 死区处理
    if np.linalg.norm([vx, vy]) < 0.01 and abs(omega) < 0.01:
        vel_cmd[:] = 0

    # 输出到 Isaac Sim 关节控制节点
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["wheel1_joint", "wheel2_joint", "wheel3_joint"]

    return True