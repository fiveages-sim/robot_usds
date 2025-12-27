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
    vel_cmd = np.zeros(4)
    

    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega = db.inputs.Desired_Angular_Velocity
    
    PI = np.pi
    wheel_positions = np.array([
        [0.21634675, 0.21634675],    
        [-0.21634675, 0.21134675],   
        [-0.21634675, -0.21134675],  
        [0.21634675, -0.21634675]    
    ])
    
    wheel_angles = np.array([
        -3 * PI / 4 - PI / 2,  # wheel1: rpy=-135度, 滚动方向=-135度+90度=-45度
        -PI / 4 - PI / 2,       # wheel2: rpy=-45度, 滚动方向=-45度+90度=45度
        PI / 4 - PI / 2,        # wheel3: rpy=45度, 滚动方向=45度+90度=135度
        3 * PI / 4 - PI / 2     # wheel4: rpy=135度, 滚动方向=135度+90度=225度=-135度
    ])
    
    for i in range(4):
        x_i, y_i = wheel_positions[i]
        theta_i = wheel_angles[i]
        
        # 万向轮速度计算：线性速度分量 + 角速度分量
        linear_component = vx * np.cos(theta_i) + vy * np.sin(theta_i)
        angular_component = omega * (x_i * np.sin(theta_i) - y_i * np.cos(theta_i))
        
        vel_cmd[i] = linear_component + angular_component
    
    vel_cmd[:] *= vel_scale
    
    if np.linalg.norm([vx, vy]) < 0.1 and abs(omega) < 0.1:
        vel_cmd[:] = 0
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["wheel1_joint", "wheel2_joint", "wheel3_joint", "wheel4_joint"]
    return True