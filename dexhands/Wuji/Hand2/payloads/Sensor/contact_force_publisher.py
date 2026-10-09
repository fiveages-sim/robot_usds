# OmniGraph ScriptNode: Wuji Hand2 contact forces → ROS2.
#
# Lives in dexhands/Wuji/Hand2/payloads/Sensor/ (Sensor=contact_force variant).
# Graph: Wuji_hand2/Graph/ROS_Contact_Force — handRoot auto-discovered from node path.
# Side/right → tfPrefix=right_hand topicPrefix=wuji_rh
# Side/left  → tfPrefix=left_hand  topicPrefix=wuji_lh
# Portable: any arm/stage that mounts this hand with Sensor=contact_force.

from __future__ import annotations

import math
from typing import Any

import numpy as np

_HAND_ROOT_DEFAULT = ""  # empty → discover from Graph prim path
_ROBOT_BASE_PRIM_DEFAULT = ""  # empty → walk ancestors for base_link
_ATTACH_MODE_DEFAULT = "link"
_TF_PREFIX_HAND_DEFAULT = "right_hand"
_TOPIC_PREFIX_DEFAULT = "wuji_rh"
_MARKER_FRAME_DEFAULT = "base_link"
_TF_DEBUG_PREFIX = "wuji_rh"  # only if publishTf
_WORLD_FRAME = "world"
_ARROW_SCALE = 0.015
_ARROW_LEN_MAX = 0.10
_MAX_FORCE_N = 50.0
_MIN_FORCE = 1e-3
_PUBLISH_TF_DEFAULT = False

_LINKS = (
    "world",
    "thumb_proximal",
    "thumb_proximal_abd",
    "thumb_middle",
    "thumb_distal",
    "index_finger_proximal",
    "index_finger_proximal_abd",
    "index_finger_middle",
    "index_finger_distal",
    "middle_finger_proximal",
    "middle_finger_proximal_abd",
    "middle_finger_middle",
    "middle_finger_distal",
    "ring_proximal",
    "ring_proximal_abd",
    "ring_middle",
    "ring_distal",
    "pinky_proximal",
    "pinky_proximal_abd",
    "pinky_middle",
    "pinky_distal",
)

_TIP_FRAMES = {
    "thumb_distal": "thumb_tip_sensor_frame",
    "index_finger_distal": "index_finger_tip_sensor_frame",
    "middle_finger_distal": "middle_finger_tip_sensor_frame",
    "ring_distal": "ring_tip_sensor_frame",
    "pinky_distal": "pinky_tip_sensor_frame",
}


def _zero_outputs(db):
    try:
        db.outputs.valid = False
        db.outputs.num_active = 0
    except Exception:
        pass


def setup(db):
    db.state.error_logged = False
    db.state.ros_node = None
    db.state.marker_pub = None
    db.state.wrench_pubs = {}
    db.state.bool_pubs = {}
    db.state.any_pub = None
    db.state.partners_pub = None
    db.state.hud_pub = None
    db.state.tf_broadcaster = None
    db.state.Marker = None
    db.state.MarkerArray = None
    db.state.WrenchStamped = None
    db.state.Bool = None
    db.state.String = None
    db.state.TransformStamped = None
    db.state.sensors = {}
    db.state.rb = None
    db.state.hand_root = None
    db.state.tick = 0
    _zero_outputs(db)


def cleanup(db):
    try:
        node = getattr(db.state, "ros_node", None)
        if node is not None:
            node.destroy_node()
    except Exception:
        pass
    db.state.ros_node = None
    db.state.marker_pub = None
    db.state.wrench_pubs = {}
    db.state.bool_pubs = {}
    db.state.any_pub = None
    db.state.partners_pub = None
    db.state.hud_pub = None
    db.state.tf_broadcaster = None
    db.state.sensors = {}
    db.state.rb = None


def _log_once(db, msg: str):
    if getattr(db.state, "error_logged", False):
        return
    db.state.error_logged = True
    print(f"[wuji_contact] {msg}")


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


def _prim(stage, path: str):
    # Always use str — mixing kit/isaac pxr Sdf.Path bindings breaks GetPrimAtPath.
    return stage.GetPrimAtPath(str(path))


def _hand_root_from_graph(db) -> str:
    """.../Wuji_hand2 from .../Wuji_hand2/Graph/ROS_Contact_Force/PublishContact."""
    try:
        node_path = str(db.node.get_prim_path())
    except Exception:
        return ""
    marker = "/Graph/"
    idx = node_path.find(marker)
    if idx > 0:
        return node_path[:idx]
    return ""


def _hand_root(db) -> str:
    root = _get_input_str(db, "handRoot", "")
    if root:
        return root.rstrip("/")
    discovered = _hand_root_from_graph(db)
    if discovered:
        return discovered.rstrip("/")
    return (_HAND_ROOT_DEFAULT or "").rstrip("/")


def _topic_prefix(db) -> str:
    p = _get_input_str(db, "topicPrefix", _TOPIC_PREFIX_DEFAULT) or _TOPIC_PREFIX_DEFAULT
    return p.strip("/")


def _topics(db):
    p = _topic_prefix(db)
    return {
        "marker": f"/{p}/contact_force_markers",
        "wrench": f"/{p}/contact_wrench",
        "in_contact": f"/{p}/in_contact",
        "any": f"/{p}/any_contact",
        "partners": f"/{p}/contact_partners",
        "hud": f"/{p}/contact_hud",
    }


def _find_base_link(hand_root: str) -> str:
    """Walk ancestors for a prim named base_link (W2 artic root)."""
    if not hand_root:
        return ""
    try:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(str(hand_root))
        while prim and prim.IsValid():
            if prim.GetName() == "base_link":
                return str(prim.GetPath())
            prim = prim.GetParent()
    except Exception:
        pass
    return ""


def _ensure_contact_report(stage, body_path: str) -> None:
    from pxr import PhysxSchema

    prim = _prim(stage, body_path)
    if not prim.IsValid():
        return
    try:
        if prim.IsInstanceProxy():
            return
    except Exception:
        pass
    if not prim.HasAPI(PhysxSchema.PhysxContactReportAPI):
        try:
            PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.0)
        except Exception:
            return
    else:
        thr = PhysxSchema.PhysxContactReportAPI(prim).GetThresholdAttr()
        if thr and thr.IsValid():
            try:
                thr.Set(0.0)
            except Exception:
                pass


def _wrap_sensor(stage, body_path: str, sensor_path: str):
    from isaacsim.sensors.experimental.physics import Contact, ContactSensor

    _ensure_contact_report(stage, body_path)
    prim = _prim(stage, sensor_path)
    try:
        if prim.IsValid() and prim.GetTypeName() == "IsaacContactSensor":
            sensor = ContactSensor(Contact(sensor_path, min_threshold=1e-4, radius=-1.0))
        else:
            sensor = ContactSensor(
                Contact.create(
                    sensor_path,
                    min_threshold=1e-4,
                    max_threshold=1e5,
                    radius=-1.0,
                )
            )
        try:
            sensor.add_raw_contact_data_to_frame()
        except Exception:
            pass
        return sensor
    except Exception as exc:
        print(f"[wuji_contact] sensor fail {sensor_path}: {exc}")
        return None


def _ensure_sensors(db) -> bool:
    if getattr(db.state, "sensors", None):
        return True
    try:
        import omni.usd
        from isaacsim.core.experimental.prims import RigidPrim
    except Exception as exc:
        _log_once(db, f"imports failed: {exc!r}")
        return False

    stage = omni.usd.get_context().get_stage()
    hand = _hand_root(db)
    db.state.hand_root = hand
    sensors = {}
    body_paths = []
    for link in _LINKS:
        body = f"{hand}/{link}"
        body_paths.append(body)
        sp = f"{body}/Contact_Sensor"
        tip_frame = _TIP_FRAMES.get(link)
        sensor = _wrap_sensor(stage, body, sp)
        if sensor is None and tip_frame:
            alt = f"{body}/{tip_frame}/TipPad_Sensor"
            sensor = _wrap_sensor(stage, body, alt)
            if sensor is None:
                sensor = _wrap_sensor(stage, body, f"{body}/{tip_frame}/Contact_Sensor")
        if sensor is not None:
            sensors[link] = sensor

    db.state.sensors = sensors
    try:
        db.state.rb = RigidPrim(body_paths)
    except Exception as exc:
        _log_once(db, f"RigidPrim poses-only failed: {exc!r}")
        db.state.rb = None

    return bool(sensors)


def _to_np(x: Any) -> np.ndarray:
    if x is None:
        return np.zeros(0)
    if hasattr(x, "numpy"):
        return np.asarray(x.numpy())
    return np.asarray(x)


def _read_poses(db) -> dict:
    out = {}
    rb = getattr(db.state, "rb", None)
    if rb is None:
        return out
    try:
        pos, orn = rb.get_world_poses()
        pos_np = _to_np(pos).reshape(-1, 3)
        orn_np = _to_np(orn).reshape(-1, 4)
        n = min(len(_LINKS), pos_np.shape[0], orn_np.shape[0])
        for i in range(n):
            out[_LINKS[i]] = (pos_np[i].astype(np.float64), orn_np[i].astype(np.float64))
    except Exception as exc:
        _log_once(db, f"get_world_poses failed: {exc!r}")
    return out




def _quat_wxyz_to_rotmat(quat_wxyz: np.ndarray) -> np.ndarray:
    w, x, y, z = [float(v) for v in np.asarray(quat_wxyz, dtype=np.float64).reshape(-1)[:4]]
    n = math.sqrt(w * w + x * x + y * y + z * z)
    if n < 1e-12:
        return np.eye(3)
    w, x, y, z = w / n, x / n, y / n, z / n
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )


def _get_prim_world_pose(prim_path: str):
    """Return (pos_xyz, quat_wxyz) of prim in Isaac stage world, or None."""
    try:
        import omni.usd
        from pxr import Usd, UsdGeom
    except Exception:
        return None
    stage = omni.usd.get_context().get_stage()
    prim = stage.GetPrimAtPath(str(prim_path))
    if not prim.IsValid():
        return None
    try:
        xform = UsdGeom.Xformable(prim)
        mat = xform.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        t = mat.ExtractTranslation()
        pos = np.array([float(t[0]), float(t[1]), float(t[2])], dtype=np.float64)
        q = mat.ExtractRotationQuat()
        # Gf.Quatd: real=w, imaginary=xyz
        imag = q.GetImaginary()
        quat = np.array(
            [float(q.GetReal()), float(imag[0]), float(imag[1]), float(imag[2])],
            dtype=np.float64,
        )
        return pos, quat
    except Exception:
        return None


def _world_to_frame(pos_w, vec_w, frame_pos, frame_quat_wxyz):
    """Express world point/vector in frame (pos, quat_wxyz)."""
    R = _quat_wxyz_to_rotmat(frame_quat_wxyz)  # world_from_local
    Rt = R.T
    p = None
    if pos_w is not None:
        p = Rt @ (np.asarray(pos_w, dtype=np.float64).reshape(3) - frame_pos)
    v = None
    if vec_w is not None:
        v = Rt @ np.asarray(vec_w, dtype=np.float64).reshape(3)
    return p, v


def _partner_short(path: str) -> str:
    if not path:
        return "?"
    parts = [p for p in str(path).split("/") if p]
    if not parts:
        return "?"
    # drop boring suffixes
    name = parts[-1]
    if name.lower() in ("mesh", "collisions", "geometry", "mesh_0", "mesh_1") and len(parts) >= 2:
        name = parts[-2]
    if len(parts) >= 2 and name == parts[-1]:
        # show parent/name when useful
        parent = parts[-2]
        if parent not in ("World", "default_environment"):
            return f"{parent}/{name}"[:40]
    return name[:40]




def _attach_mode(db) -> str:
    m = (_get_input_str(db, "attachMode", _ATTACH_MODE_DEFAULT) or _ATTACH_MODE_DEFAULT).strip().lower()
    if m in ("link", "base_link", "base", "world"):
        return "base_link" if m == "base" else m
    return _ATTACH_MODE_DEFAULT


def _hand_tf_prefix(db) -> str:
    return (_get_input_str(db, "tfPrefix", _TF_PREFIX_HAND_DEFAULT) or _TF_PREFIX_HAND_DEFAULT).rstrip("_")


def _ros_link_frame(isaac_link: str, prefix: str) -> str:
    """Map Isaac Hand2 link name → fa_w2_ws / wuji_description TF frame."""
    if isaac_link == "world":
        # Isaac palm rigid body; URDF palm mesh lives on wrist
        return f"{prefix}_wrist"
    return f"{prefix}_{isaac_link}"

def _marker_frame_name(db) -> str:
    return _get_input_str(db, "markerFrame", _MARKER_FRAME_DEFAULT) or _MARKER_FRAME_DEFAULT


def _robot_base_prim(db) -> str:
    explicit = _get_input_str(db, "robotBasePrim", "")
    if explicit:
        return explicit
    if _ROBOT_BASE_PRIM_DEFAULT:
        return _ROBOT_BASE_PRIM_DEFAULT
    return _find_base_link(_hand_root(db))


def _as_vec3(value) -> np.ndarray:
    if value is None:
        return np.zeros(3)
    if isinstance(value, dict):
        return np.array(
            [float(value.get("x", 0.0)), float(value.get("y", 0.0)), float(value.get("z", 0.0))],
            dtype=np.float64,
        )
    try:
        v = np.asarray(value, dtype=np.float64).reshape(-1)
        if v.size < 3:
            return np.zeros(3)
        return v[:3].copy()
    except Exception:
        return np.zeros(3)


def _impulse_to_force_vec(impulse, contact_dt: float) -> np.ndarray:
    """Convert raw impulse (N·s) → force (N) using the contact's own dt (not physics-step dt)."""
    v = _as_vec3(impulse)
    dt = float(contact_dt or 0.0)
    if dt > 1e-9:
        return v / dt
    # Fallback: Isaac tests often assume 60 Hz when dt missing
    return v * 60.0


def _path_from_body_id(body_id) -> str:
    try:
        from pxr import PhysicsSchemaTools

        return str(PhysicsSchemaTools.intToSdfPath(int(body_id)))
    except Exception:
        return ""


def _other_body(hand: str, body0: str, body1: str) -> str:
    b0, b1 = str(body0), str(body1)
    if b0.startswith(hand):
        return b1
    if b1.startswith(hand):
        return b0
    return b1 or b0


def _read_link_contact(sensor, hand: str, negate_force: bool = True):
    """Returns (force_world, contact_pos_or_None, force_mag, in_contact, partner_paths).

    Magnitude: prefer ContactSensorReading.value (Isaac already impulse/dt correctly).
    Direction: from raw impulses using each contact's own ``dt``; then scale to |value|.
    Do NOT sum impulses with OnPhysicsStep dt — that caused giant one-sided arrows.
    """
    force = np.zeros(3)
    pos = None
    mag = 0.0
    in_contact = False
    partners = []

    try:
        reading = sensor.get_sensor_reading()
        mag = float(getattr(reading, "value", 0.0) or 0.0)
        in_contact = bool(getattr(reading, "in_contact", False))
    except Exception:
        reading = None

    try:
        raw = sensor.get_raw_data() or []
    except Exception:
        raw = []

    if raw:
        in_contact = True
        dir_acc = np.zeros(3)
        best_f = -1.0
        best_pos = None
        peak_from_raw = 0.0
        seen = set()
        for c in raw:
            fvec = _impulse_to_force_vec(c.get("impulse"), float(c.get("dt") or 0.0))
            fmag = float(np.linalg.norm(fvec))
            peak_from_raw = max(peak_from_raw, fmag)
            # direction: sum unit vectors so many soft contacts don't inflate magnitude
            if fmag > 1e-12:
                dir_acc += fvec / fmag
            p = _as_vec3(c.get("position"))
            if fmag > best_f and float(np.linalg.norm(p)) > 0.0:
                best_f = fmag
                best_pos = p
            b0 = c.get("body0")
            b1 = c.get("body1")
            if isinstance(b0, (int, float)) or (isinstance(b0, str) and str(b0).isdigit()):
                b0 = _path_from_body_id(b0)
            if isinstance(b1, (int, float)) or (isinstance(b1, str) and str(b1).isdigit()):
                b1 = _path_from_body_id(b1)
            other = _other_body(hand, str(b0 or ""), str(b1 or ""))
            if other and other not in seen:
                seen.add(other)
                partners.append(other)

        pos = best_pos
        # Prefer Isaac reading.value; raw peak only as fallback (same as schematic max)
        if mag <= _MIN_FORCE:
            mag = peak_from_raw
        dnorm = float(np.linalg.norm(dir_acc))
        if dnorm > 1e-12 and mag > _MIN_FORCE:
            force = (dir_acc / dnorm) * mag
        elif mag > _MIN_FORCE and best_pos is not None:
            # no direction — leave force zero (green contact sphere only)
            force = np.zeros(3)
    elif in_contact or mag > 0.0:
        in_contact = True

    # Clamp unreliable PhysX spikes (deep penetration / solver pop)
    if mag > _MAX_FORCE_N:
        scale = _MAX_FORCE_N / mag
        force = force * scale
        mag = _MAX_FORCE_N

    # PhysX impulse convention → force *on the finger*. Right hand needs negate;
    # mirrored left mesh/Side often already matches "on finger" — controlled by
    # inputs:negateForce (Side/right=1, Side/left=0).
    if negate_force:
        force = -force

    return force, pos, mag, in_contact, partners


def _negate_force(db) -> bool:
    """True → flip impulse to force-on-finger (RH). LH Side sets negateForce=0."""
    if hasattr(db.inputs, "negateForce"):
        try:
            v = getattr(db.inputs, "negateForce", None)
            if v is not None:
                return _get_input_bool(db, "negateForce", True)
        except Exception:
            pass
    prefix = _hand_tf_prefix(db).lower()
    if prefix.startswith("left"):
        return False
    return True


def _ensure_ros(db) -> bool:
    if getattr(db.state, "marker_pub", None) is not None:
        return True
    try:
        import rclpy
        from geometry_msgs.msg import TransformStamped, WrenchStamped
        from std_msgs.msg import Bool, String
        from tf2_ros import TransformBroadcaster
        from visualization_msgs.msg import Marker, MarkerArray
    except Exception as exc:
        _log_once(db, f"rclpy import failed: {exc!r}")
        return False

    try:
        if not rclpy.ok():
            rclpy.init(args=None)
    except Exception:
        pass

    try:
        topics = _topics(db)
        db.state.topics = topics
        node_name = f"wuji_contact_force_{_topic_prefix(db).replace('/', '_')}"
        node = rclpy.create_node(node_name)
        marker_pub = node.create_publisher(MarkerArray, topics["marker"], 10)
        any_pub = node.create_publisher(Bool, topics["any"], 10)
        partners_pub = node.create_publisher(String, topics["partners"], 10)
        hud_pub = node.create_publisher(MarkerArray, topics["hud"], 10)
        wrench_pubs = {}
        bool_pubs = {}
        for link in _LINKS:
            wrench_pubs[link] = node.create_publisher(
                WrenchStamped, f"{topics['wrench']}/{link}", 10
            )
            bool_pubs[link] = node.create_publisher(
                Bool, f"{topics['in_contact']}/{link}", 10
            )
        tf_br = TransformBroadcaster(node)
    except Exception as exc:
        _log_once(db, f"ROS pub create failed: {exc!r}")
        return False

    db.state.ros_node = node
    db.state.marker_pub = marker_pub
    db.state.any_pub = any_pub
    db.state.partners_pub = partners_pub
    db.state.hud_pub = hud_pub
    db.state.wrench_pubs = wrench_pubs
    db.state.bool_pubs = bool_pubs
    db.state.tf_broadcaster = tf_br
    db.state.Marker = Marker
    db.state.MarkerArray = MarkerArray
    db.state.WrenchStamped = WrenchStamped
    db.state.Bool = Bool
    db.state.String = String
    db.state.TransformStamped = TransformStamped
    return True


def _stamp_from_sim(db):
    try:
        t = float(getattr(db.inputs, "simulationTime", 0.0) or 0.0)
    except Exception:
        t = 0.0
    sec = int(math.floor(t))
    nsec = int(round((t - sec) * 1e9))
    if nsec >= 1_000_000_000:
        sec += 1
        nsec -= 1_000_000_000
    return sec, max(0, nsec)


def _publish(db, poses, link_data, sec: int, nsec: int):
    if not _ensure_ros(db):
        return 0

    publish_tf = _get_input_bool(db, "publishTf", _PUBLISH_TF_DEFAULT)
    mode = _attach_mode(db)
    hand_prefix = _hand_tf_prefix(db)
    base_prim = _robot_base_prim(db)

    # base_link mode: one shared frame (legacy; drifts if chassis slips vs OCS2 TF)
    frame_pos = np.zeros(3)
    frame_quat = np.array([1.0, 0.0, 0.0, 0.0])
    shared_frame = _WORLD_FRAME
    if mode == "base_link":
        shared_frame = _marker_frame_name(db)
        frame_pose = _get_prim_world_pose(base_prim)
        if frame_pose is None:
            _log_once(db, f"robot base pose missing ({base_prim}); fallback world")
            mode = "world"
            shared_frame = _WORLD_FRAME
        else:
            frame_pos, frame_quat = frame_pose
    elif mode == "world":
        shared_frame = _WORLD_FRAME

    Marker = db.state.Marker
    MarkerArray = db.state.MarkerArray
    WrenchStamped = db.state.WrenchStamped
    TransformStamped = db.state.TransformStamped
    Bool = db.state.Bool
    String = db.state.String

    if publish_tf:
        for link, (pos, quat) in poses.items():
            msg = TransformStamped()
            msg.header.stamp.sec = sec
            msg.header.stamp.nanosec = nsec
            msg.header.frame_id = _WORLD_FRAME
            msg.child_frame_id = f"{_TF_DEBUG_PREFIX}/{link}"
            msg.transform.translation.x = float(pos[0])
            msg.transform.translation.y = float(pos[1])
            msg.transform.translation.z = float(pos[2])
            msg.transform.rotation.w = float(quat[0])
            msg.transform.rotation.x = float(quat[1])
            msg.transform.rotation.y = float(quat[2])
            msg.transform.rotation.z = float(quat[3])
            try:
                db.state.tf_broadcaster.sendTransform(msg)
            except Exception:
                pass

    arr = MarkerArray()
    hud = MarkerArray()
    # DELETEALL ignores frame_id in RViz — one is enough
    clear = Marker()
    clear.action = Marker.DELETEALL
    clear.header.frame_id = shared_frame if mode != "link" else f"{hand_prefix}_wrist"
    clear.header.stamp.sec = sec
    clear.header.stamp.nanosec = nsec
    arr.markers.append(clear)
    hud.markers.append(clear)

    active = 0
    mid = 0
    hid = 0
    any_contact = False
    partner_bits = []
    hud_lines = []

    for link, (force_w, cpos_w, mag, in_contact, partners) in link_data.items():
        if in_contact:
            any_contact = True
        shorts = [_partner_short(p) for p in partners]
        for p in partners:
            partner_bits.append(f"{link}={p}")

        bmsg = Bool()
        bmsg.data = bool(in_contact)
        try:
            db.state.bool_pubs[link].publish(bmsg)
        except Exception:
            pass

        # Resolve pose frame for this link
        if mode == "link":
            ros_frame = _ros_link_frame(link, hand_prefix)
            if link not in poses:
                # still publish empty wrench
                force = np.zeros(3)
                start = None
            else:
                link_pos, link_quat = poses[link]
                pos_w = cpos_w if cpos_w is not None else link_pos
                start, force = _world_to_frame(pos_w, force_w, link_pos, link_quat)
                if force is None:
                    force = np.zeros(3)
        elif mode == "base_link":
            ros_frame = shared_frame
            _, force = _world_to_frame(None, force_w, frame_pos, frame_quat)
            if force is None:
                force = np.zeros(3)
            if cpos_w is not None:
                pos_w = cpos_w
            elif link in poses:
                pos_w = poses[link][0]
            else:
                pos_w = None
            start = None
            if pos_w is not None:
                start, _ = _world_to_frame(pos_w, None, frame_pos, frame_quat)
        else:
            ros_frame = _WORLD_FRAME
            force = np.asarray(force_w, dtype=np.float64).reshape(3)
            if cpos_w is not None:
                start = np.asarray(cpos_w, dtype=np.float64).reshape(3)
            elif link in poses:
                start = poses[link][0]
            else:
                start = None

        wmsg = WrenchStamped()
        wmsg.header.stamp.sec = sec
        wmsg.header.stamp.nanosec = nsec
        wmsg.header.frame_id = ros_frame
        if mag > _MIN_FORCE:
            wmsg.wrench.force.x = float(force[0])
            wmsg.wrench.force.y = float(force[1])
            wmsg.wrench.force.z = float(force[2])
        try:
            db.state.wrench_pubs[link].publish(wmsg)
        except Exception:
            pass

        if not in_contact or start is None:
            continue

        # Green sphere at contact (in finger / base / world frame)
        s = Marker()
        s.header.frame_id = ros_frame
        s.header.stamp.sec = sec
        s.header.stamp.nanosec = nsec
        s.ns = "wuji_rh_in_contact"
        s.id = mid
        mid += 1
        s.type = Marker.SPHERE
        s.action = Marker.ADD
        s.pose.position.x = float(start[0])
        s.pose.position.y = float(start[1])
        s.pose.position.z = float(start[2])
        s.pose.orientation.w = 1.0
        s.scale.x = s.scale.y = s.scale.z = 0.008
        s.color.r, s.color.g, s.color.b, s.color.a = 0.2, 1.0, 0.35, 0.95
        s.lifetime.nanosec = 200_000_000
        arr.markers.append(s)
        active += 1

        partner_txt = ",".join(shorts) if shorts else "?"
        label = f"{link}\n{mag:.2f} N\n→ {partner_txt}"
        hud_lines.append(f"{link}:{mag:.2f}N->{partner_txt}")

        tmark = Marker()
        tmark.header.frame_id = ros_frame
        tmark.header.stamp.sec = sec
        tmark.header.stamp.nanosec = nsec
        tmark.ns = "wuji_rh_force_text"
        tmark.id = hid
        hid += 1
        tmark.type = Marker.TEXT_VIEW_FACING
        tmark.action = Marker.ADD
        tmark.pose.position.x = float(start[0])
        tmark.pose.position.y = float(start[1])
        tmark.pose.position.z = float(start[2] + 0.02)
        tmark.pose.orientation.w = 1.0
        tmark.scale.z = 0.018
        tmark.color.r, tmark.color.g, tmark.color.b, tmark.color.a = 1.0, 1.0, 0.85, 0.95
        tmark.text = label
        tmark.lifetime.nanosec = 200_000_000
        arr.markers.append(tmark)
        hud.markers.append(tmark)

        fnorm = float(np.linalg.norm(force))
        if fnorm <= _MIN_FORCE:
            continue

        direction = force / fnorm
        length = min(mag * _ARROW_SCALE, _ARROW_LEN_MAX)
        end = start + direction * length

        m = Marker()
        m.header.frame_id = ros_frame
        m.header.stamp.sec = sec
        m.header.stamp.nanosec = nsec
        m.ns = "wuji_rh_force"
        m.id = mid
        mid += 1
        m.type = Marker.ARROW
        m.action = Marker.ADD
        m.scale.x = 0.004
        m.scale.y = 0.008
        m.scale.z = 0.0
        t = min(1.0, mag / 25.0)
        m.color.r = 0.2 + 0.8 * t
        m.color.g = 0.85 * (1.0 - 0.5 * t)
        m.color.b = 0.2
        m.color.a = 0.95
        from geometry_msgs.msg import Point

        p0 = Point()
        p0.x, p0.y, p0.z = float(start[0]), float(start[1]), float(start[2])
        p1 = Point()
        p1.x, p1.y, p1.z = float(end[0]), float(end[1]), float(end[2])
        m.points = [p0, p1]
        m.lifetime.nanosec = 200_000_000
        arr.markers.append(m)

    amsg = Bool()
    amsg.data = bool(any_contact)
    try:
        db.state.any_pub.publish(amsg)
    except Exception:
        pass

    pmsg = String()
    pmsg.data = ";".join(partner_bits)
    try:
        db.state.partners_pub.publish(pmsg)
    except Exception:
        pass

    # HUD on palm / wrist frame
    if hud_lines:
        if mode == "link":
            hud_frame = f"{hand_prefix}_wrist"
            palm_local = np.array([0.0, 0.0, 0.08], dtype=np.float64)
        elif mode == "base_link" and "world" in poses:
            hud_frame = shared_frame
            palm_w = poses["world"][0]
            palm_local, _ = _world_to_frame(palm_w, None, frame_pos, frame_quat)
            if palm_local is None:
                palm_local = np.zeros(3)
            palm_local = palm_local + np.array([0.0, 0.0, 0.12])
        elif "world" in poses:
            hud_frame = _WORLD_FRAME
            palm_local = poses["world"][0] + np.array([0.0, 0.0, 0.12])
        else:
            palm_local = None
            hud_frame = shared_frame
        if palm_local is not None:
            board = Marker()
            board.header.frame_id = hud_frame
            board.header.stamp.sec = sec
            board.header.stamp.nanosec = nsec
            board.ns = "wuji_rh_hud_board"
            board.id = 0
            board.type = Marker.TEXT_VIEW_FACING
            board.action = Marker.ADD
            board.pose.position.x = float(palm_local[0])
            board.pose.position.y = float(palm_local[1])
            board.pose.position.z = float(palm_local[2])
            board.pose.orientation.w = 1.0
            board.scale.z = 0.022
            board.color.r, board.color.g, board.color.b, board.color.a = 0.9, 1.0, 0.9, 0.95
            board.text = f"RH contact [{mode}]\n" + "\n".join(hud_lines[:8])
            board.lifetime.nanosec = 200_000_000
            arr.markers.append(board)
            hud.markers.append(board)

    try:
        db.state.marker_pub.publish(arr)
    except Exception as exc:
        _log_once(db, f"marker publish failed: {exc!r}")
    try:
        if getattr(db.state, "hud_pub", None) is not None:
            db.state.hud_pub.publish(hud)
    except Exception:
        pass
    return active


def compute(db):
    if not _ensure_sensors(db):
        _zero_outputs(db)
        return
    if not _ensure_ros(db):
        _zero_outputs(db)
        return

    hand = db.state.hand_root or _hand_root(db)
    poses = _read_poses(db)
    negate = _negate_force(db)
    link_data = {}
    for link, sensor in db.state.sensors.items():
        force, cpos, mag, in_contact, partners = _read_link_contact(sensor, hand, negate)
        link_data[link] = (force, cpos, mag, in_contact, partners)

    sec, nsec = _stamp_from_sim(db)
    active = _publish(db, poses, link_data, sec, nsec)

    try:
        db.outputs.valid = True
        db.outputs.num_active = int(active)
    except Exception:
        pass

    db.state.tick = getattr(db.state, "tick", 0) + 1
