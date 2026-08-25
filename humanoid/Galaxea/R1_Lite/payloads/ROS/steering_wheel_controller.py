# OmniGraph ScriptNode for Galaxea_R1_Lite tri-steer chassis.
# Inputs: Desired_Linear_Velocity_{X,Y}, Desired_Angular_Velocity, linearGain, angularGain, flipVelocityScale
# Outputs: Steer_* (position), Wheel_* (velocity)

import numpy as np

# Match Copy/R1 convention: wheel speed scale ~50; angular gain default 1
# Match SteerChassis: ω ≈ v / r with r≈0.07 → ~14.3 (not 50)
_DEFAULT_LINEAR_GAIN = 14.3
_DEFAULT_ANGULAR_GAIN = 1.0
_DEFAULT_FLIP_VELOCITY_SCALE = 0.35

_SPEED_EPS = 1e-6
_NUM_WHEELS = 3

# Lite chassis steer motor XY (Z ignored for planar IK)
_WHEEL_POSITIONS = np.array(
    [
        [0.29183, 0.0],  # wheel1 / steer_joint1
        [-0.16817, 0.24],  # wheel2 / steer_joint2
        [-0.16817, -0.24],  # wheel3 / steer_joint3
    ]
)

_prev_pos_cmd = np.zeros(_NUM_WHEELS)
_prev_vel_unscaled = np.zeros(_NUM_WHEELS)
_has_prev_steer = False


def _wrap_to_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def _angle_diff(target, reference):
    return _wrap_to_pi(target - reference)


def _pick_steer_and_wheel_speed(raw_angle, speed, ref_angle):
    # (theta, v) and (theta+pi, -v) are equivalent; pick smaller steer delta vs ref.
    a = _wrap_to_pi(raw_angle)
    va = speed
    b = _wrap_to_pi(raw_angle + np.pi)
    vb = -speed
    da = abs(_angle_diff(a, ref_angle))
    db = abs(_angle_diff(b, ref_angle))
    if db < da:
        return b, vb
    return a, va


def setup(db):
    global _prev_pos_cmd, _prev_vel_unscaled, _has_prev_steer
    _prev_pos_cmd = np.zeros(_NUM_WHEELS)
    _prev_vel_unscaled = np.zeros(_NUM_WHEELS)
    _has_prev_steer = False


def cleanup(db):
    global _has_prev_steer, _prev_vel_unscaled
    _has_prev_steer = False
    _prev_vel_unscaled = np.zeros(_NUM_WHEELS)


def compute(db):
    global _prev_pos_cmd, _prev_vel_unscaled, _has_prev_steer

    linear_gain = float(getattr(db.inputs, "linearGain", _DEFAULT_LINEAR_GAIN))
    angular_gain = float(getattr(db.inputs, "angularGain", _DEFAULT_ANGULAR_GAIN))
    flip_vel_scale = float(getattr(db.inputs, "flipVelocityScale", _DEFAULT_FLIP_VELOCITY_SCALE))
    flip_vel_scale = max(0.0, min(1.0, flip_vel_scale))

    pos_cmd = np.zeros(_NUM_WHEELS)
    vel_cmd = np.zeros(_NUM_WHEELS)

    vx = db.inputs.Desired_Linear_Velocity_X
    vy = db.inputs.Desired_Linear_Velocity_Y
    omega_cmd = db.inputs.Desired_Angular_Velocity
    omega = omega_cmd * angular_gain

    for i in range(_NUM_WHEELS):
        x_i, y_i = _WHEEL_POSITIONS[i]
        vx_total = vx + (-omega * y_i)
        vy_total = vy + (omega * x_i)
        angle = np.arctan2(vy_total, vx_total)
        speed = np.linalg.norm([vx_total, vy_total])

        if speed < _SPEED_EPS:
            pos_cmd[i] = _prev_pos_cmd[i] if _has_prev_steer else 0.0
            vel_cmd[i] = 0.0
        else:
            ref = _prev_pos_cmd[i] if _has_prev_steer else 0.0
            pos_cmd[i], vel_cmd[i] = _pick_steer_and_wheel_speed(angle, speed, ref)
            if _has_prev_steer:
                pv = _prev_vel_unscaled[i]
                nv = vel_cmd[i]
                if (
                    abs(pv) > _SPEED_EPS
                    and abs(nv) > _SPEED_EPS
                    and pv * nv < 0
                    and flip_vel_scale < 1.0
                ):
                    vel_cmd[i] *= flip_vel_scale

    vel_cmd[:] *= linear_gain

    if np.linalg.norm([vx, vy]) < 0.0001 and abs(omega_cmd) < 0.0001:
        pos_cmd[:] = 0
        vel_cmd[:] = 0

    inv_gain = 1.0 / linear_gain if linear_gain != 0.0 else 0.0
    _prev_vel_unscaled = vel_cmd * inv_gain
    _prev_pos_cmd = pos_cmd.copy()
    _has_prev_steer = True

    db.outputs.Steer_Position_Command = pos_cmd
    db.outputs.Steer_Joints = ["steer_joint1", "steer_joint2", "steer_joint3"]
    db.outputs.Wheel_Velocity_Command = vel_cmd
    db.outputs.Wheel_Joints = ["wheel_joint1", "wheel_joint2", "wheel_joint3"]
    return True
