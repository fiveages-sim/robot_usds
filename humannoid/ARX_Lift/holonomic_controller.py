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
    vel_cmd = np.zeros(3)
    

    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega = db.inputs.Desired_Angular_Velocity
    
    wheel_positions = np.array([
        [0.182349, 0.315838],
        [0.182349, -0.315838],
        [-0.364699, 0.0]
    ])
    
    PI = np.pi
    wheel_angles = np.array([
        -2 * PI / 3 - PI / 2,  # wheel1: rpy=-120度, 滚动方向=-120度+90度=-30度
        2 * PI / 3 - PI / 2,   # wheel2: rpy=120度, 滚动方向=120度+90度=210度=-150度
        -PI / 2                 # wheel3: rpy=0度, 滚动方向=0度+90度=90度
    ])
    
    for i in range(3):
        x_i, y_i = wheel_positions[i]
        theta_i = wheel_angles[i]
        
        linear_component = vx * np.cos(theta_i) + vy * np.sin(theta_i)
        angular_component = omega * (x_i * np.sin(theta_i) - y_i * np.cos(theta_i))
        
        vel_cmd[i] = linear_component + angular_component
    
    vel_cmd[:] *= vel_scale
    
    if np.linalg.norm([vx, vy]) < 0.1 and abs(omega) < 0.1:
        vel_cmd[:] = 0
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["wheel1_joint", "wheel2_joint", "wheel3_joint"]
    return True