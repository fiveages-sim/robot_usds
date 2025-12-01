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
    pos_cmd = np.zeros(4)
    vel_cmd = np.zeros(4)
    

    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega = db.inputs.Desired_Angular_Velocity
    
    wheel_positions = np.array([
        [0.241, 0.185],   # fl
        [-0.253, 0.185],  # fr
        [-0.253, -0.185], # rr  
        [0.241, -0.185]    # rl 
    ])
    
    # 对每个轮子计算速度
    for i in range(4):
        x_i, y_i = wheel_positions[i]
        

        vx_angular = -omega * y_i 
        vy_angular = omega * x_i
     
        vx_total = vx + vx_angular
        vy_total = vy + vy_angular
        
        pos_cmd[i] = np.arctan2(vy_total, vx_total)
        
        vel_cmd[i] = np.linalg.norm([vx_total, vy_total])
    
    vel_cmd[:] *= vel_scale
    
    if np.linalg.norm([vx, vy]) < 0.1 and abs(omega) < 0.1:
        pos_cmd[0] = np.arctan2(1, -1) 
        pos_cmd[1] = np.arctan2(-1, -1)  
        pos_cmd[2] = np.arctan2(-1, 1) 
        pos_cmd[3] = np.arctan2(1, 1)  
        
        vel_cmd[:] = 0
    
    db.outputs.Steer_Position_Command = pos_cmd
    db.outputs.Steer_Joints = ["fl_steering_joint","rl_steering_joint","rr_steering_joint","fr_steering_joint"]
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["fl_wheel","rl_wheel","rr_wheel","fr_wheel"]
    return True