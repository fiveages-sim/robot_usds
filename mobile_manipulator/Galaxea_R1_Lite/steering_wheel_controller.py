# This script is executed the first time the script node computes, or the next time
# it computes after this script is modified or the 'Reset' button is pressed.
#
# The following callback functions may be defined in this script:
#     setup(db): Called immediately after this script is executed
#     compute(db): Called every time the node computes (should always be defined)
#     cleanup(db): Called when the node is deleted or the reset button is pressed
# Available variables:
#    db: og.Database The node interface, attributes are exposed like db.inputs.foo
#                    Use db.log_error, db.log_warning to report problems.
#    og: The omni.graph.core module

import numpy as np

def setup(db: og.Database):
    pass


def cleanup(db: og.Database):
    pass


def compute(db: og.Database):
    vel_scale = 50
    pos_cmd = np.zeros(3)
    vel_cmd = np.zeros(3)
    

    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega = db.inputs.Desired_Angular_Velocity
    
    # 根据 chassis.xacro 中的关节位置定义三舵轮位置
    wheel_positions = np.array([
        [0.29183, 0],   # wheel1 (steer_joint1)
        [-0.16817, 0.24],     # wheel2 (steer_joint2)
        [-0.16817, -0.24]     # wheel3 (steer_joint3)
    ])
    
    # 对每个轮子计算速度
    for i in range(3):
        x_i, y_i = wheel_positions[i]
        

        vx_angular = -omega * y_i 
        vy_angular = omega * x_i
     
        vx_total = vx + vx_angular
        vy_total = vy + vy_angular
        
        # 计算原始角度
        angle = np.arctan2(vy_total, vx_total)
        
        # 将角度限制在正负90度范围内
        # 如果角度超出范围，通过vel_cmd的符号来补偿
        if angle > np.pi / 2:
            pos_cmd[i] = angle - np.pi
            vel_cmd[i] = -np.linalg.norm([vx_total, vy_total])
        elif angle < -np.pi / 2:
            pos_cmd[i] = angle + np.pi
            vel_cmd[i] = -np.linalg.norm([vx_total, vy_total])
        else:
            pos_cmd[i] = angle
            vel_cmd[i] = np.linalg.norm([vx_total, vy_total])
    
    vel_cmd[:] *= vel_scale
    
    if np.linalg.norm([vx, vy]) < 0.1 and abs(omega) < 0.1:
        pos_cmd[0] = 0.0  # wheel1 向前
        pos_cmd[1] = 0.0  # wheel2 向前
        pos_cmd[2] = 0.0  # wheel3 向前
        
        vel_cmd[:] = 0
    
    db.outputs.Steer_Position_Command = pos_cmd
    db.outputs.Steer_Joints = ["steer_joint1", "steer_joint2", "steer_joint3"]
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["wheel_joint1", "wheel_joint2", "wheel_joint3"]
    return True