# OmniGraph ScriptNode: read EE AssemblerFixedJoint 6D wrench and publish
# geometry_msgs/WrenchStamped via rclpy.
#
# Paths come from OmniGraph relationship targets (rel inputs:robotPrim /
# inputs:jointPrim). USD remaps </CR5/...> under /World/CR5.
#
# Gravity compensation (enableGravityComp): sum MassAPI masses under EE
# (gripper tool), express gravity about tcp link origin (includes flange
# offset), after transporting the measured joint wrench into the tcp frame.
#
# Isaac note: get_measured_joint_forces(joint_names=...) is broken; use
# joint_index + 1 with joint_indices (IsaacSim issue #100).

from __future__ import annotations

import numpy as np

_FRAME_ID = "tcp"
_DEFAULT_TOPIC = "/isaac/ft_wrench"
_G = 9.81


def _zero_outputs(db):
    db.outputs.frame_id = _FRAME_ID
    db.outputs.stamp_sec = 0
    db.outputs.stamp_nanosec = 0
    db.outputs.force_x = 0.0
    db.outputs.force_y = 0.0
    db.outputs.force_z = 0.0
    db.outputs.torque_x = 0.0
    db.outputs.torque_y = 0.0
    db.outputs.torque_z = 0.0
    db.outputs.valid = False


def setup(db):
    db.state.arti = None
    db.state.arti_path = None
    db.state.force_row_index = None
    db.state.joint_prim_path_cached = None
    db.state.error_logged = False
    db.state.ros_node = None
    db.state.ros_pub = None
    db.state.WrenchStamped = None
    db.state.ee_mass = None
    db.state.ee_mass_root = None
    db.state.gravity_comp_logged = False
    _zero_outputs(db)


def _log_once(db, msg: str):
    if getattr(db.state, "error_logged", False):
        return
    db.state.error_logged = True
    print(f"[ft_wrench_publisher] {msg}")


def _get_input_str(db, name: str, default: str = "") -> str:
    try:
        v = getattr(db.inputs, name, None)
        if v:
            return str(v)
    except Exception:
        pass
    return default


def _get_input_bool(db, name: str, default: bool = False) -> bool:
    try:
        v = getattr(db.inputs, name, None)
        if v is None:
            return default
        return bool(v)
    except Exception:
        return default


def _first_path(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        return str(value[0])
    return str(value)


def _get_rel_prim_path(db, attr_name: str) -> str:
    try:
        path = _first_path(getattr(db.inputs, attr_name, None))
        if path:
            return path
    except Exception:
        pass

    try:
        attr = db.node.get_attribute(f"inputs:{attr_name}")
        path = _first_path(attr.get())
        if path:
            return path
    except Exception:
        pass

    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(db.node.get_prim_path())
        rel = prim.GetRelationship(f"inputs:{attr_name}")
        if rel and rel.HasAuthoredTargets():
            targets = rel.GetTargets()
            if targets:
                return str(targets[0])
        if rel:
            targets = rel.GetForwardedTargets()
            if targets:
                return str(targets[0])
    except Exception:
        pass

    return ""


def _robot_path_from_graph(db) -> str:
    try:
        node_path = str(db.node.get_prim_path())
    except Exception:
        return ""
    marker = "/Graph/"
    idx = node_path.find(marker)
    if idx > 0:
        return node_path[:idx]
    return ""


def _resolve_robot_prim_path(db) -> str:
    path = _get_rel_prim_path(db, "robotPrim")
    if path:
        return path
    path = _robot_path_from_graph(db)
    if path:
        return path
    _log_once(db, "robotPrim relationship empty and graph fallback failed")
    return ""


def _resolve_joint_prim_path(db) -> str:
    path = _get_rel_prim_path(db, "jointPrim")
    if path:
        return path
    _log_once(db, "jointPrim relationship empty")
    return ""


def _joint_name_from_prim_path(joint_prim_path: str) -> str:
    path = joint_prim_path.strip().rstrip("/")
    if not path:
        return ""
    return path.rsplit("/", 1)[-1]


def _ee_root_from_joint_path(joint_prim_path: str) -> str:
    # .../Link6/tcp/EE/gripper_base/AssemblerFixedJoint -> .../Link6/tcp/EE
    path = joint_prim_path.strip().rstrip("/")
    marker = "/EE/"
    idx = path.find(marker)
    if idx >= 0:
        return path[: idx + len("/EE")]
    parts = path.split("/")
    if len(parts) >= 3:
        return "/".join(parts[:-2])
    return ""


def _build_articulation(robot_prim_path: str):
    from isaacsim.core.prims import Articulation as A

    if not robot_prim_path:
        return None
    try:
        return A(prim_paths_expr=robot_prim_path)
    except TypeError:
        return A(robot_prim_path)


def _ensure_articulation(db):
    robot_prim_path = _resolve_robot_prim_path(db)
    if not robot_prim_path:
        return None

    arti = getattr(db.state, "arti", None)
    cached_path = getattr(db.state, "arti_path", None)
    if arti is None or cached_path != robot_prim_path:
        arti = _build_articulation(robot_prim_path)
        if arti is None:
            _log_once(db, f"failed to create Articulation at {robot_prim_path}")
            return None
        arti.initialize()
        db.state.arti = arti
        db.state.arti_path = robot_prim_path
        db.state.force_row_index = None
        db.state.joint_prim_path_cached = None
        db.state.ee_mass = None
        db.state.ee_mass_root = None

    try:
        if hasattr(arti, "is_physics_handle_valid") and not arti.is_physics_handle_valid():
            arti.initialize()
            db.state.force_row_index = None
    except Exception:
        pass

    return db.state.arti


def _lookup_joint_index(arti, joint_name: str):
    if hasattr(arti, "get_joint_index"):
        try:
            return int(arti.get_joint_index(joint_name))
        except Exception:
            pass

    meta = getattr(arti, "_metadata", None)
    if meta is not None:
        indices = getattr(meta, "joint_indices", None)
        if indices is not None and joint_name in indices:
            return int(indices[joint_name])

    if hasattr(arti, "get_joint_indices"):
        try:
            idxs = np.asarray(arti.get_joint_indices([joint_name])).reshape(-1)
            if idxs.size:
                return int(idxs[0])
        except Exception:
            pass
    return None


def _ensure_force_row_index(db, arti, joint_prim_path: str):
    cached_path = getattr(db.state, "joint_prim_path_cached", None)
    cached_idx = getattr(db.state, "force_row_index", None)
    if cached_idx is not None and cached_path == joint_prim_path:
        return cached_idx

    joint_name = _joint_name_from_prim_path(joint_prim_path)
    if not joint_name:
        return None

    joint_index = _lookup_joint_index(arti, joint_name)
    if joint_index is None:
        _log_once(
            db,
            f"joint '{joint_name}' not found in articulation metadata "
            f"(path={joint_prim_path})",
        )
        return None

    force_row_index = int(joint_index) + 1
    db.state.force_row_index = force_row_index
    db.state.joint_prim_path_cached = joint_prim_path
    return force_row_index


def _read_wrench(db, arti, joint_prim_path: str):
    force_row_index = _ensure_force_row_index(db, arti, joint_prim_path)
    if force_row_index is None:
        return None

    forces = arti.get_measured_joint_forces(joint_indices=[force_row_index])
    w = np.asarray(forces, dtype=np.float64)
    w = np.squeeze(w)
    if w.shape == (6,):
        return w
    if w.ndim >= 1 and w.shape[-1] == 6:
        return w.reshape(-1, 6)[0]
    _log_once(db, f"unexpected force shape: {getattr(w, 'shape', None)}")
    return None


def _get_world_transform(prim_path: str):
    try:
        from pxr import UsdGeom
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsValid():
            return None
        return UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(0.0)
    except Exception:
        return None


def _quat_wxyz_to_gf(q):
    from pxr import Gf

    return Gf.Quatd(float(q[0]), Gf.Vec3d(float(q[1]), float(q[2]), float(q[3])))


def _read_vec3_attr(prim, name: str, default=(0.0, 0.0, 0.0)):
    attr = prim.GetAttribute(name)
    if attr and attr.HasAuthoredValueOpinion():
        v = attr.Get()
        if v is not None:
            return (float(v[0]), float(v[1]), float(v[2]))
    return default


def _read_quat_attr(prim, name: str, default=(1.0, 0.0, 0.0, 0.0)):
    attr = prim.GetAttribute(name)
    if attr and attr.HasAuthoredValueOpinion():
        q = attr.Get()
        if q is not None:
            return (float(q[0]), float(q[1]), float(q[2]), float(q[3]))
    return default


def _rel_first_target(prim, rel_name: str) -> str:
    rel = prim.GetRelationship(rel_name)
    if not rel:
        return ""
    targets = rel.GetTargets()
    if not targets:
        return ""
    return str(targets[0])


def _local_pose_matrix(local_pos, local_rot_wxyz):
    from pxr import Gf

    m = Gf.Matrix4d()
    m.SetTransform(Gf.Rotation(_quat_wxyz_to_gf(local_rot_wxyz)), Gf.Vec3d(*local_pos))
    return m


def _joint_body_frames(joint_prim_path: str):
    # Returns (world_from_tcp, world_from_joint) or (None, None).
    # tcp = physics:body0 link frame (origin at tcp prim).
    # joint = body1 * localPose1 (AssemblerFixedJoint measure point / flange face).
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        joint_prim = stage.GetPrimAtPath(joint_prim_path)
        if not joint_prim or not joint_prim.IsValid():
            return None, None

        body0_path = _rel_first_target(joint_prim, "physics:body0")
        body1_path = _rel_first_target(joint_prim, "physics:body1")
        if not body1_path:
            parent = joint_prim.GetParent()
            body1_path = str(parent.GetPath()) if parent else ""
        if not body0_path:
            # Fallback: .../tcp/EE/... -> .../tcp
            ee = _ee_root_from_joint_path(joint_prim_path)
            if ee.endswith("/EE"):
                body0_path = ee[: -len("/EE")]

        world_from_tcp = _get_world_transform(body0_path) if body0_path else None
        world_from_body1 = _get_world_transform(body1_path) if body1_path else None
        if world_from_body1 is None:
            return None, None

        local_pos1 = _read_vec3_attr(joint_prim, "physics:localPos1")
        local_rot1 = _read_quat_attr(joint_prim, "physics:localRot1")
        world_from_joint = _local_pose_matrix(local_pos1, local_rot1) * world_from_body1
        return world_from_tcp, world_from_joint
    except Exception:
        return None, None


def _gf_rotation_matrix(world_from_frame):
    # 3x3 numpy: v_world_col = R @ v_frame_col
    r = world_from_frame.ExtractRotationMatrix()
    return np.array(
        [
            [r[0][0], r[0][1], r[0][2]],
            [r[1][0], r[1][1], r[1][2]],
            [r[2][0], r[2][1], r[2][2]],
        ],
        dtype=np.float64,
    )


def _wrench_joint_to_tcp(wrench_joint, world_from_tcp, world_from_joint):
    # Transport measured joint wrench into tcp link frame about tcp origin.
    # Includes flange offset: p_joint_in_tcp = localPos0 when body0=tcp.
    f_j = np.asarray(wrench_joint[:3], dtype=np.float64)
    t_j = np.asarray(wrench_joint[3:6], dtype=np.float64)

    R_wj = _gf_rotation_matrix(world_from_joint)
    R_wt = _gf_rotation_matrix(world_from_tcp)
    R_tj = R_wt.T @ R_wj  # joint vectors -> tcp vectors

    tj = world_from_joint.ExtractTranslation()
    tt = world_from_tcp.ExtractTranslation()
    p_joint_world = np.array([tj[0], tj[1], tj[2]], dtype=np.float64)
    p_tcp_world = np.array([tt[0], tt[1], tt[2]], dtype=np.float64)
    p_joint_in_tcp = R_wt.T @ (p_joint_world - p_tcp_world)

    f_t = R_tj @ f_j
    t_t = R_tj @ t_j + np.cross(p_joint_in_tcp, f_t)
    return np.concatenate([f_t, t_t])


def _collect_ee_mass_bodies(ee_root_path: str):
    bodies = []
    try:
        from pxr import Usd, UsdPhysics
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        root = stage.GetPrimAtPath(ee_root_path)
        if not root or not root.IsValid():
            return bodies

        for prim in Usd.PrimRange(root):
            if not prim.HasAPI(UsdPhysics.MassAPI):
                continue
            mass_api = UsdPhysics.MassAPI(prim)
            mass_attr = mass_api.GetMassAttr()
            if not mass_attr or not mass_attr.HasAuthoredValueOpinion():
                continue
            mass = float(mass_attr.Get() or 0.0)
            if mass <= 0.0:
                continue
            com = np.zeros(3, dtype=np.float64)
            com_attr = mass_api.GetCenterOfMassAttr()
            if com_attr and com_attr.HasAuthoredValueOpinion():
                c = com_attr.Get()
                if c is not None:
                    com = np.array([c[0], c[1], c[2]], dtype=np.float64)
            bodies.append((str(prim.GetPath()), mass, com))
    except Exception:
        return bodies
    return bodies


def _ensure_ee_mass_cache(db, joint_prim_path: str):
    ee_root = _ee_root_from_joint_path(joint_prim_path)
    if not ee_root:
        return None
    if getattr(db.state, "ee_mass_root", None) == ee_root and getattr(db.state, "ee_mass", None) is not None:
        return db.state.ee_mass

    bodies = _collect_ee_mass_bodies(ee_root)
    db.state.ee_mass_root = ee_root
    db.state.ee_mass = bodies
    if not getattr(db.state, "gravity_comp_logged", False):
        total = sum(b[1] for b in bodies)
        print(
            f"[ft_wrench_publisher] gravity comp EE='{ee_root}' "
            f"bodies={len(bodies)} mass={total:.4f} kg (frame=tcp)"
        )
        db.state.gravity_comp_logged = True
    return bodies


def _tool_gravity_in_tcp(db, joint_prim_path: str, world_from_tcp):
    # Gravity wrench ON the EE tool, about tcp origin, in tcp axes.
    # Flange offset is included via COM relative to tcp origin.
    from pxr import Gf

    bodies = _ensure_ee_mass_cache(db, joint_prim_path)
    if not bodies or world_from_tcp is None:
        return None

    tcp_from_world = world_from_tcp.GetInverse()
    total_mass = 0.0
    mass_moment = Gf.Vec3d(0.0, 0.0, 0.0)

    for prim_path, mass, com_local in bodies:
        body_world = _get_world_transform(prim_path)
        if body_world is None:
            continue
        com_body = Gf.Vec3d(float(com_local[0]), float(com_local[1]), float(com_local[2]))
        com_world = body_world.Transform(com_body)
        com_tcp = tcp_from_world.Transform(com_world)
        total_mass += mass
        mass_moment += com_tcp * mass

    if total_mass <= 0.0:
        return None

    com_tcp = mass_moment / total_mass
    g_world = Gf.Vec3d(0.0, 0.0, -_G)
    g_tcp = tcp_from_world.TransformDir(g_world)
    force = g_tcp * total_mass
    torque = Gf.Cross(com_tcp, force)
    return np.array(
        [force[0], force[1], force[2], torque[0], torque[1], torque[2]],
        dtype=np.float64,
    )


def _wrench_in_tcp_with_gravity_comp(db, joint_prim_path: str, wrench_joint):
    # 1) Move measured joint wrench into tcp link frame (accounts for flange offset).
    # 2) Optionally remove EE tool gravity expressed in the same tcp frame.
    world_from_tcp, world_from_joint = _joint_body_frames(joint_prim_path)
    if world_from_tcp is None or world_from_joint is None:
        return np.asarray(wrench_joint, dtype=np.float64)

    wrench_tcp = _wrench_joint_to_tcp(wrench_joint, world_from_tcp, world_from_joint)

    if not _get_input_bool(db, "enableGravityComp", True):
        return wrench_tcp

    g_on_tool_tcp = _tool_gravity_in_tcp(db, joint_prim_path, world_from_tcp)
    if g_on_tool_tcp is None:
        return wrench_tcp

    # Incoming joint force on child ≈ -gravity_on_tool when hanging.
    # After expressing both in tcp: F_ext = F_meas_tcp + F_gravity_on_tool_tcp
    sign = 1.0
    try:
        sign = float(getattr(db.inputs, "gravityCompSign", 1.0))
    except Exception:
        sign = 1.0
    if sign == 0.0:
        sign = 1.0

    return wrench_tcp + sign * g_on_tool_tcp


def _ensure_ros_publisher(db):
    if getattr(db.state, "ros_pub", None) is not None:
        return True

    try:
        import rclpy
        from geometry_msgs.msg import WrenchStamped
    except Exception as exc:
        _log_once(db, f"rclpy/geometry_msgs import failed: {exc!r}")
        return False

    try:
        if not rclpy.ok():
            rclpy.init(args=None)
    except Exception:
        pass

    topic = _get_input_str(db, "topicName", _DEFAULT_TOPIC)
    if topic and not topic.startswith("/"):
        topic = "/" + topic

    try:
        node = rclpy.create_node("cr5_ft_wrench_publisher")
        pub = node.create_publisher(WrenchStamped, topic, 10)
    except Exception as exc:
        _log_once(db, f"failed to create ROS publisher on {topic}: {exc!r}")
        return False

    db.state.ros_node = node
    db.state.ros_pub = pub
    db.state.WrenchStamped = WrenchStamped
    print(f"[ft_wrench_publisher] publishing WrenchStamped on {topic}")
    return True


def _publish_wrench(db, sec: int, nanosec: int, wrench):
    if not _ensure_ros_publisher(db):
        return

    msg = db.state.WrenchStamped()
    msg.header.frame_id = _FRAME_ID
    msg.header.stamp.sec = int(sec)
    msg.header.stamp.nanosec = int(nanosec)
    if wrench is not None:
        msg.wrench.force.x = float(wrench[0])
        msg.wrench.force.y = float(wrench[1])
        msg.wrench.force.z = float(wrench[2])
        msg.wrench.torque.x = float(wrench[3])
        msg.wrench.torque.y = float(wrench[4])
        msg.wrench.torque.z = float(wrench[5])
    try:
        db.state.ros_pub.publish(msg)
    except Exception as exc:
        _log_once(db, f"publish failed: {exc!r}")


def compute(db):
    _zero_outputs(db)

    sim_t = 0.0
    try:
        sim_t = float(db.inputs.simulationTime)
    except Exception:
        pass

    sec = int(sim_t)
    nanosec = int(round((sim_t - sec) * 1e9))
    if nanosec >= 1_000_000_000:
        sec += 1
        nanosec -= 1_000_000_000

    db.outputs.stamp_sec = sec
    db.outputs.stamp_nanosec = nanosec
    db.outputs.frame_id = _FRAME_ID

    wrench = None
    try:
        arti = _ensure_articulation(db)
        if arti is not None:
            joint_prim_path = _resolve_joint_prim_path(db)
            wrench = _read_wrench(db, arti, joint_prim_path)
            if wrench is not None:
                wrench = _wrench_in_tcp_with_gravity_comp(db, joint_prim_path, wrench)
                db.outputs.force_x = float(wrench[0])
                db.outputs.force_y = float(wrench[1])
                db.outputs.force_z = float(wrench[2])
                db.outputs.torque_x = float(wrench[3])
                db.outputs.torque_y = float(wrench[4])
                db.outputs.torque_z = float(wrench[5])
                db.outputs.valid = True
    except Exception as exc:
        _log_once(db, f"compute failed: {exc!r}")

    _publish_wrench(db, sec, nanosec, wrench)


def cleanup(db):
    arti = getattr(db.state, "arti", None)
    if arti is not None:
        try:
            if hasattr(arti, "destroy"):
                arti.destroy()
        except Exception:
            pass
    db.state.arti = None
    db.state.arti_path = None
    db.state.force_row_index = None
    db.state.joint_prim_path_cached = None
    db.state.ee_mass = None
    db.state.ee_mass_root = None

    ros_node = getattr(db.state, "ros_node", None)
    if ros_node is not None:
        try:
            ros_node.destroy_node()
        except Exception:
            pass
    db.state.ros_node = None
    db.state.ros_pub = None
    db.state.WrenchStamped = None
