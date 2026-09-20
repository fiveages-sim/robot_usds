# OmniGraph ScriptNode: read EE AssemblerFixedJoint 6D wrench and publish
# geometry_msgs/WrenchStamped via rclpy.
#
# Lives with the reusable KWR75B sensor asset (sensors/6Dof F&T Sensor/).
# Graph is under the sensor prim; paths auto-discover:
#   sensor root = .../KWR75B  (prefix before /Graph/)
#   tcp         = sibling .../link7/tcp
#   arm mount   = parent of link7 (Marvin / Left_Arm / Right_Arm)
# Articulation: walk ancestors for PhysicsArticulationRootAPI (W2 body base_link).
# Optional rel inputs:robotPrim / inputs:jointPrim override discovery.
#
# Force row: match fixed-joint body1 (gripper_base) against articulation
# link_paths — required on dual-arm W2 where both EEs are named AssemblerFixedJoint.
# Gravity compensation: off by default (enableGravityComp); tcp-frame mass sum
# was misleading on Tianji flange orientation.
#
# Sensor Side=left/right (owned by KWR75B.usda) sets topicName/frameId.
#
from __future__ import annotations

import numpy as np

_DEFAULT_FRAME_ID = "tcp"
_DEFAULT_TOPIC = "/isaac/ft_wrench"
_G = 9.81


def _frame_id(db) -> str:
    return _get_input_str(db, "frameId", _DEFAULT_FRAME_ID) or _DEFAULT_FRAME_ID


def _zero_outputs(db):
    db.outputs.frame_id = _frame_id(db)
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
    db.state.force_row_logged = False
    db.state.error_logged = False
    db.state.ros_node = None
    db.state.ros_pub = None
    db.state.ros_topic = None
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


def _sensor_root_from_graph(db) -> str:
    """.../KWR75B from .../KWR75B/Graph/ROS_FT_Sensor/ReadFT."""
    try:
        node_path = str(db.node.get_prim_path())
    except Exception:
        return ""
    marker = "/Graph/"
    idx = node_path.find(marker)
    if idx > 0:
        return node_path[:idx]
    return ""


def _robot_path_from_graph(db) -> str:
    # Legacy name: return arm mount (parent of flange link), not sensor root.
    sensor = _sensor_root_from_graph(db)
    if not sensor:
        return ""
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        sensor_prim = stage.GetPrimAtPath(sensor)
        if not sensor_prim or not sensor_prim.IsValid():
            return sensor
        link = sensor_prim.GetParent()  # typically link7
        if link and link.IsValid():
            arm = link.GetParent()
            if arm and arm.IsValid() and str(arm.GetPath()) not in ("", "/"):
                return str(arm.GetPath())
            return str(link.GetPath())
    except Exception:
        pass
    return sensor


def _resolve_arm_prim_path(db) -> str:
    """Arm mount prim (Marvin / Left_Arm / Right_Arm). Used for artic walk start."""
    path = _get_rel_prim_path(db, "robotPrim")
    if path:
        return path
    path = _robot_path_from_graph(db)
    if path:
        return path
    _log_once(db, "robotPrim empty and graph-based arm discovery failed")
    return ""


def _resolve_robot_prim_path(db) -> str:
    return _resolve_arm_prim_path(db)


def _has_articulation_root_api(prim) -> bool:
    if not prim or not prim.IsValid():
        return False
    try:
        from pxr import UsdPhysics

        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            return True
    except Exception:
        pass
    try:
        schemas = [str(s) for s in prim.GetAppliedSchemas()]
        return any("ArticulationRoot" in s for s in schemas)
    except Exception:
        return False


def _articulation_candidates_from(start_path: str):
    """Find PhysicsArticulationRootAPI prims near the arm mount.

    W2: Left_Arm/Right_Arm are NOT articulations — root is on
    /World/FiveAges_W2/base_link. Never return the arm mount path unless it
    itself carries ArticulationRootAPI (standalone Marvin with active root_joint).
    """
    if not start_path:
        return []
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(start_path)
    except Exception:
        return []

    ordered = []
    seen = set()

    def _add(path: str):
        if path and path not in seen and path != "/":
            seen.add(path)
            ordered.append(path)

    def _consider(p):
        if not p or not p.IsValid():
            return
        if _has_articulation_root_api(p):
            _add(str(p.GetPath()))
            parent = p.GetParent()
            # Isaac Articulation often wants the robot Xform that owns the root API.
            if parent and parent.IsValid() and str(parent.GetPath()) not in ("", "/"):
                _add(str(parent.GetPath()))

    while prim and prim.IsValid():
        path = str(prim.GetPath())
        if path == "/":
            break
        _consider(prim)
        try:
            for child in prim.GetChildren():
                _consider(child)
        except Exception:
            pass
        prim = prim.GetParent()

    # Do NOT fall back to start_path — constructing Articulation(Left_Arm) on W2
    # registers a broken physics view and asserts in _on_physics_ready.
    return ordered


def _build_articulation(robot_prim_path: str):
    from isaacsim.core.prims import Articulation as A

    if not robot_prim_path:
        return None
    try:
        return A(prim_paths_expr=robot_prim_path)
    except TypeError:
        return A(robot_prim_path)


def _ensure_articulation(db):
    arm_prim_path = _resolve_arm_prim_path(db)
    if not arm_prim_path:
        return None

    candidates = _articulation_candidates_from(arm_prim_path)
    if not candidates:
        _log_once(
            db,
            f"no PhysicsArticulationRootAPI found walking from '{arm_prim_path}' "
            f"(W2 arms are not articulations; expected body base_link)",
        )
        return None

    cached_path = getattr(db.state, "arti_path", None)
    arti = getattr(db.state, "arti", None)

    if arti is not None and cached_path in candidates:
        try:
            if hasattr(arti, "is_physics_handle_valid") and not arti.is_physics_handle_valid():
                arti.initialize()
                db.state.force_row_index = None
            return arti
        except Exception:
            db.state.arti = None
            db.state.arti_path = None

    last_err = None
    for cand in candidates:
        arti = None
        try:
            arti = _build_articulation(cand)
            if arti is None:
                continue
            arti.initialize()
            # Reject views that never bound a backend (W2 Left_Arm pattern).
            view = getattr(arti, "_physics_view", None)
            if view is not None:
                backend = getattr(view, "_backend", None)
                if backend is None:
                    raise RuntimeError(f"articulation view has no backend at {cand}")
            db.state.arti = arti
            db.state.arti_path = cand
            db.state.force_row_index = None
            db.state.joint_prim_path_cached = None
            db.state.force_row_logged = False
            db.state.ee_mass = None
            db.state.ee_mass_root = None
            if cand != arm_prim_path:
                print(
                    f"[ft_wrench_publisher] articulation at '{cand}' "
                    f"(arm mount was '{arm_prim_path}')"
                )
            return arti
        except Exception as exc:
            last_err = exc
            # Drop failed handle so its _on_physics_ready cannot assert later.
            try:
                if arti is not None and hasattr(arti, "destroy"):
                    arti.destroy()
            except Exception:
                pass
            continue

    _log_once(
        db,
        f"failed to create Articulation from candidates {candidates}: {last_err!r}",
    )
    return None


def _discover_assembler_joint_under(tcp_path: str) -> str:
    """Find active <tcp>/<EE>/gripper_base/AssemblerFixedJoint (any EE name)."""
    if not tcp_path:
        return ""
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        tcp = stage.GetPrimAtPath(tcp_path)
        if not tcp or not tcp.IsValid():
            return ""
        for child in tcp.GetChildren():
            joint = stage.GetPrimAtPath(
                f"{child.GetPath()}/gripper_base/AssemblerFixedJoint"
            )
            if joint and joint.IsValid() and joint.IsActive():
                return str(joint.GetPath())
    except Exception:
        return ""
    return ""


def _resolve_joint_prim_path(db) -> str:
    path = _get_rel_prim_path(db, "jointPrim")
    if not path:
        sensor = _sensor_root_from_graph(db)
        if sensor:
            # Flange tcp is sibling of sensor under the same link (link7/tcp).
            parent = sensor.rsplit("/", 1)[0]
            path = f"{parent}/tcp" if parent else ""
        if not path:
            arm = _resolve_arm_prim_path(db)
            if arm:
                path = f"{arm.rstrip('/')}/link7/tcp"
            else:
                _log_once(db, "jointPrim empty and tcp discovery failed")
                return ""

    if path.rstrip("/").endswith("AssemblerFixedJoint"):
        return path

    discovered = _discover_assembler_joint_under(path)
    if discovered:
        return discovered

    # EE not mounted yet — silent until an EE variant is selected.
    return ""


def _joint_name_from_prim_path(joint_prim_path: str) -> str:
    path = joint_prim_path.strip().rstrip("/")
    if not path:
        return ""
    return path.rsplit("/", 1)[-1]


def _ee_root_from_joint_path(joint_prim_path: str) -> str:
    # .../link7/tcp/AG2F120S/gripper_base/AssemblerFixedJoint -> .../tcp/AG2F120S
    # Also supports legacy .../tcp/EE/gripper_base/AssemblerFixedJoint
    path = joint_prim_path.strip().rstrip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 3 and parts[-1] == "AssemblerFixedJoint" and parts[-2] == "gripper_base":
        return "/" + "/".join(parts[:-2])
    marker = "/EE/"
    idx = path.find(marker)
    if idx >= 0:
        return path[: idx + len("/EE")]
    if len(parts) >= 3:
        return "/" + "/".join(parts[:-2])
    return ""


def _normalize_prim_path(path: str) -> str:
    return (path or "").strip().rstrip("/")


def _link_paths_list(arti):
    """Return flat list of link USD paths for artic instance 0."""
    view = getattr(arti, "_physics_view", None)
    if view is None:
        return []
    try:
        paths = view.link_paths
    except Exception:
        paths = None
    if paths is None:
        return []
    # Backend may return [[env0_links...], ...] or a flat list.
    try:
        if len(paths) > 0 and isinstance(paths[0], (list, tuple)):
            return [str(p) for p in paths[0]]
        return [str(p) for p in paths]
    except Exception:
        return []


def _match_path_index(paths, target_path: str):
    """Exact or unique suffix/prefix match of target_path in paths."""
    target = _normalize_prim_path(target_path)
    if not target or not paths:
        return None

    norm = [_normalize_prim_path(p) for p in paths]
    for i, p in enumerate(norm):
        if p == target:
            return i

    # Unique suffix match (handles World/ vs without, remapped roots).
    hits = []
    for i, p in enumerate(norm):
        if p.endswith(target) or target.endswith(p):
            hits.append(i)
    if len(hits) == 1:
        return hits[0]

    # Unique match on last N path segments (e.g. Left_Arm/.../gripper_base).
    parts = [s for s in target.split("/") if s]
    for n in range(min(6, len(parts)), 1, -1):
        suffix = "/" + "/".join(parts[-n:])
        hits = [i for i, p in enumerate(norm) if p.endswith(suffix)]
        if len(hits) == 1:
            return hits[0]
    return None


def _child_link_path_from_joint(joint_prim_path: str) -> str:
    """AssemblerFixedJoint body1 (gripper_base) — unique on dual-arm W2."""
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        joint_prim = stage.GetPrimAtPath(joint_prim_path)
        if not joint_prim or not joint_prim.IsValid():
            return ""
        body1 = _rel_first_target(joint_prim, "physics:body1")
        if body1:
            return body1
        parent = joint_prim.GetParent()
        return str(parent.GetPath()) if parent else ""
    except Exception:
        return ""


def _lookup_joint_index(arti, joint_name: str):
    """Legacy short-name lookup (ambiguous when names collide)."""
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
    """Force buffer row for this EE mount.

    Prefer matching the fixed-joint *child link* (body1 / gripper_base) against
    articulation link_paths — unique on W2 dual-arm where both sides are named
    AssemblerFixedJoint. Measured forces are "link incoming joint" rows, so the
    link index is the force row (no +1).

    Fallback: short joint name +1 (CR5 / Isaac issue #100), only if the name is
    unique in metadata.
    """
    cached_path = getattr(db.state, "joint_prim_path_cached", None)
    cached_idx = getattr(db.state, "force_row_index", None)
    if cached_idx is not None and cached_path == joint_prim_path:
        return cached_idx

    link_path = _child_link_path_from_joint(joint_prim_path)
    link_paths = _link_paths_list(arti)
    link_idx = _match_path_index(link_paths, link_path) if link_path else None
    if link_idx is not None:
        db.state.force_row_index = int(link_idx)
        db.state.joint_prim_path_cached = joint_prim_path
        if not getattr(db.state, "force_row_logged", False):
            print(
                f"[ft_wrench_publisher] force row via link_paths: "
                f"row={link_idx} link='{link_path}' joint='{joint_prim_path}'"
            )
            db.state.force_row_logged = True
        return db.state.force_row_index

    # Fallback: unique short joint name only.
    joint_name = _joint_name_from_prim_path(joint_prim_path)
    meta = getattr(arti, "_metadata", None)
    names = list(getattr(meta, "joint_names", None) or [])
    if joint_name and names.count(joint_name) == 1:
        joint_index = _lookup_joint_index(arti, joint_name)
        if joint_index is not None:
            force_row_index = int(joint_index) + 1
            db.state.force_row_index = force_row_index
            db.state.joint_prim_path_cached = joint_prim_path
            if not getattr(db.state, "force_row_logged", False):
                print(
                    f"[ft_wrench_publisher] force row via unique joint name: "
                    f"row={force_row_index} name='{joint_name}' "
                    f"(link_paths miss for '{link_path}')"
                )
                db.state.force_row_logged = True
            return force_row_index

    _log_once(
        db,
        f"cannot resolve force row for joint='{joint_prim_path}' "
        f"link='{link_path}' (duplicate short names or link_paths miss)",
    )
    return None


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
            # Fallback: .../tcp/<EE>/... -> .../tcp
            ee = _ee_root_from_joint_path(joint_prim_path)
            if "/tcp/" in ee:
                body0_path = ee.rsplit("/", 1)[0]
            elif ee.endswith("/EE"):
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

    if not _get_input_bool(db, "enableGravityComp", False):
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


def _topic_name(db) -> str:
    topic = _get_input_str(db, "topicName", _DEFAULT_TOPIC) or _DEFAULT_TOPIC
    if topic and not topic.startswith("/"):
        topic = "/" + topic
    return topic


def _destroy_ros_publisher(db):
    ros_node = getattr(db.state, "ros_node", None)
    if ros_node is not None:
        try:
            ros_node.destroy_node()
        except Exception:
            pass
    db.state.ros_node = None
    db.state.ros_pub = None
    db.state.ros_topic = None
    db.state.WrenchStamped = None


def _ensure_ros_publisher(db):
    topic = _topic_name(db)
    if getattr(db.state, "ros_pub", None) is not None and getattr(db.state, "ros_topic", None) == topic:
        return True

    _destroy_ros_publisher(db)

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

    # Unique node per arm/side so dual-arm stages do not clash.
    safe = topic.strip("/").replace("/", "_") or "ft_wrench"
    node_name = f"marvin_ft_wrench_{safe}"

    try:
        node = rclpy.create_node(node_name)
        pub = node.create_publisher(WrenchStamped, topic, 10)
    except Exception as exc:
        _log_once(db, f"failed to create ROS publisher on {topic}: {exc!r}")
        return False

    db.state.ros_node = node
    db.state.ros_pub = pub
    db.state.ros_topic = topic
    db.state.WrenchStamped = WrenchStamped
    print(f"[ft_wrench_publisher] publishing WrenchStamped on {topic} (node={node_name})")
    return True


def _publish_wrench(db, sec: int, nanosec: int, wrench):
    if not _ensure_ros_publisher(db):
        return

    msg = db.state.WrenchStamped()
    msg.header.frame_id = _frame_id(db)
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

    frame = _frame_id(db)
    db.outputs.stamp_sec = sec
    db.outputs.stamp_nanosec = nanosec
    db.outputs.frame_id = frame

    wrench = None
    try:
        arti = _ensure_articulation(db)
        if arti is not None:
            joint_prim_path = _resolve_joint_prim_path(db)
            if joint_prim_path:
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
    _destroy_ros_publisher(db)
