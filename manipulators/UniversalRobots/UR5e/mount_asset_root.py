# SPDX-FileCopyrightText: Copyright (c) 2026 FiveAges
# SPDX-License-Identifier: Apache-2.0
"""Mount an Isaac asset-root-relative USD onto this prim when the stage opens.

Reads ``customData["fasim_asset_root_rel_path"]`` (e.g.
``Isaac/Robots_Multiphysics/UniversalRobots/ur5e/ur5e.usda``), resolves it
with ``get_assets_root_path()`` (honors ``ISAACSIM_ASSET_REGION_PROFILE`` /
``ISAACSIM_ASSET_ROOT``), and authors a payload on the session edit target.

Do not hardcode ``https://omniverse-content-production...`` URLs in USDA.
"""

from __future__ import annotations

import math

import carb
from omni.behavior.scripting.core import BehaviorScript
from pxr import Sdf, Usd


_REL_PATH_KEY = "fasim_asset_root_rel_path"
_DEFAULT_REL_PATH = "Isaac/Robots_Multiphysics/UniversalRobots/ur5e/ur5e.usda"
# Env layers set customData["fasim_initial_joint_pose"] = "home_1" so the
# viewport shows the pose before Play (joint state attrs alone do not FK the
# link xforms until physics starts / robot.poser teleports).
_INITIAL_POSE_KEY = "fasim_initial_joint_pose"
_HOME_POSES_RAD = {
    # ocs2_arm_controller / ros2_controllers.yaml home_1 (RoboAPI Home).
    "home_1": {
        "shoulder_pan_joint": -0.5580,
        "shoulder_lift_joint": -1.6481,
        "elbow_joint": 1.6395,
        "wrist_1_joint": -1.5622,
        "wrist_2_joint": -1.5708,
        "wrist_3_joint": -0.5580,
    },
    # fiveages_acepro2: home_1 with shoulder_pan_joint - 90 deg.
    "home_1_j1p90": {
        "shoulder_pan_joint": -0.5579963267948966,
        "shoulder_lift_joint": -1.6481,
        "elbow_joint": 1.6395,
        "wrist_1_joint": -1.5622,
        "wrist_2_joint": -1.5708,
        "wrist_3_joint": -0.5580,
    },
}


def _payload_asset_paths(prim) -> list[str]:
    op = prim.GetMetadata("payload")
    if not op:
        return []
    if hasattr(op, "GetAddedOrExplicitItems"):
        return [str(p.assetPath) for p in op.GetAddedOrExplicitItems()]
    paths: list[str] = []
    for attr in ("explicitItems", "prependedItems", "addedItems"):
        items = getattr(op, attr, None) or []
        paths.extend(str(p.assetPath) for p in items)
    return paths


def _join_asset_root(root: str, rel: str) -> str:
    return f"{root.rstrip('/')}/{rel.lstrip('/')}"


def _is_official_mount(path: str, rel: str, full: str) -> bool:
    """True if ``path`` is a resolved mount of the official ``rel`` asset.

    Local wrapper payloads such as ``./payloads/ROS/fiveages.usda`` must not match.
    """
    if path == full:
        return True
    rel_norm = rel.lstrip("/")
    normalized = path.replace("\\", "/").rstrip("/")
    if not normalized.endswith("/" + rel_norm) and normalized != rel_norm:
        return False
    return "://" in path or normalized.startswith("/") or normalized.startswith("omniverse:")


def _resolve_asset_root():
    from isaacsim.storage.native import get_assets_root_path

    return get_assets_root_path()


def _joint_dict_for_pose(prim, pose_name: str) -> dict[str, float]:
    """Map joint prim paths under ``prim`` to radians for a named pose."""
    joints = _HOME_POSES_RAD.get(pose_name)
    if not joints:
        return {}
    stage = prim.GetStage()
    if stage is None:
        return {}
    root = str(prim.GetPath())
    out: dict[str, float] = {}
    for name, rad in joints.items():
        path = f"{root}/joints/{name}"
        joint = stage.GetPrimAtPath(path)
        if joint and joint.IsValid():
            out[path] = float(rad)
        else:
            carb.log_warn(f"MountAssetRoot: joint missing for pose {pose_name}: {path}")
    return out


def _set_joint_attrs_deg(stage, joint_dict_rad: dict[str, float]) -> None:
    """Write drive target + joint state in degrees (PhysX USD convention)."""
    for path, rad in joint_dict_rad.items():
        joint = stage.GetPrimAtPath(path)
        if not joint or not joint.IsValid():
            continue
        deg = float(math.degrees(rad))
        for attr_name in (
            "drive:angular:physics:targetPosition",
            "state:angular:physics:position",
        ):
            attr = joint.GetAttribute(attr_name)
            if not attr:
                attr = joint.CreateAttribute(attr_name, Sdf.ValueTypeNames.Float)
            attr.Set(deg)
        vel = joint.GetAttribute("state:angular:physics:velocity")
        if not vel:
            vel = joint.CreateAttribute(
                "state:angular:physics:velocity", Sdf.ValueTypeNames.Float
            )
        vel.Set(0.0)


def _apply_initial_joint_pose(prim, pose_name: str) -> None:
    """Teleport link xforms to ``pose_name`` so the viewport matches before Play.

    Prefers ``isaacsim.robot.poser.apply_joint_state`` (FK into USD). Falls back
    to writing joint state/drive attrs only if poser is unavailable.
    """
    pose_name = (pose_name or "").strip()
    if not pose_name:
        return
    joint_dict = _joint_dict_for_pose(prim, pose_name)
    if not joint_dict:
        if pose_name not in _HOME_POSES_RAD:
            carb.log_warn(
                f"MountAssetRoot: unknown {_INITIAL_POSE_KEY}={pose_name!r} on {prim.GetPath()}"
            )
        return

    stage = prim.GetStage()
    try:
        from isaacsim.robot.poser import apply_joint_state

        apply_joint_state(stage, prim, joint_dict)
        carb.log_info(
            f"MountAssetRoot: teleported {prim.GetPath()} to {pose_name} via robot.poser"
        )
        return
    except Exception as exc:  # noqa: BLE001 — poser may be unloaded or lack RobotAPI
        carb.log_warn(
            f"MountAssetRoot: robot.poser teleport failed for {pose_name} on "
            f"{prim.GetPath()}: {exc}; writing joint attrs only"
        )
    _set_joint_attrs_deg(stage, joint_dict)


def _mount_rel_on_prim(prim, rel: str, asset_root: str) -> None:
    if not rel:
        carb.log_error(f"MountAssetRoot: empty {_REL_PATH_KEY} on {prim.GetPath()}")
        return
    full = _join_asset_root(asset_root, rel)
    current = _payload_asset_paths(prim)
    stale = [path for path in current if _is_official_mount(path, rel, full)]
    if stale == [full] and current.count(full) == 1:
        carb.log_info(f"MountAssetRoot: already mounted {full} -> {prim.GetPath()}")
        return

    payloads = prim.GetPayloads()
    # Only replace previous official mounts of this rel path. Do not
    # ClearPayloads(): ROS/EE payloads on the same prim must stay.
    for path in stale:
        payloads.RemovePayload(Sdf.Payload(path))
    payloads.AddPayload(Sdf.Payload(full))
    carb.log_info(f"MountAssetRoot: mounted {full} -> {prim.GetPath()} (was {current})")


class MountAssetRoot(BehaviorScript):
    def on_init(self):
        prim = self.prim
        if not prim or not prim.IsValid():
            carb.log_error(f"MountAssetRoot: invalid prim at {self.prim_path}")
            return

        try:
            asset_root = _resolve_asset_root()
        except Exception as exc:  # noqa: BLE001 — surface any root-resolve failure
            carb.log_error(
                f"MountAssetRoot: get_assets_root_path failed for {self.prim_path}: {exc}"
            )
            return

        if not asset_root:
            carb.log_error(f"MountAssetRoot: empty asset root for {self.prim_path}")
            return

        rel = (prim.GetCustomDataByKey(_REL_PATH_KEY) or _DEFAULT_REL_PATH).strip()

        # Collect child mounts BEFORE authoring the official robot payload.
        # Adding a payload on this prim can recompose the stage mid-callback.
        child_mounts: list[tuple[str, str]] = []
        stage = prim.GetStage()
        for child in Usd.PrimRange(prim):
            if child == prim or not child.IsValid():
                continue
            child_rel = child.GetCustomDataByKey(_REL_PATH_KEY)
            if child_rel:
                child_mounts.append((str(child.GetPath()), str(child_rel).strip()))
        # Known EE site if the range missed a variant-composed prim.
        for suffix in (
            "wrist_3_link/flange/tool0/EE",
            "flange/tool0/EE",
            "tool0/EE",
        ):
            path = f"{prim.GetPath()}/{suffix}"
            child = stage.GetPrimAtPath(path) if stage is not None else None
            if child and child.IsValid():
                child_rel = child.GetCustomDataByKey(_REL_PATH_KEY)
                if child_rel and all(path != existing for existing, _ in child_mounts):
                    child_mounts.append((path, str(child_rel).strip()))

        carb.log_info(f"MountAssetRoot: child mounts at {self.prim_path}: {child_mounts}")
        _mount_rel_on_prim(prim, rel, asset_root)
        self._mount_child_list(stage, child_mounts, asset_root)
        self._last_ee = self._ee_selection(prim)
        self._pose_pending = True
        self._apply_pose_from_custom_data(prim)
        self._subscribe_timeline_stop()

    def _apply_pose_from_custom_data(self, prim) -> bool:
        pose = prim.GetCustomDataByKey(_INITIAL_POSE_KEY)
        if not pose:
            self._pose_pending = False
            return False
        joint_dict = _joint_dict_for_pose(prim, str(pose))
        if not joint_dict:
            # Joints may not be composed yet; retry from on_update.
            return False
        _apply_initial_joint_pose(prim, str(pose))
        self._pose_pending = False
        return True

    def _subscribe_timeline_stop(self) -> None:
        """Re-teleport after Stop so reset-to-zero xforms do not stick in the viewport."""
        if getattr(self, "_timeline_sub", None) is not None:
            return
        try:
            import omni.timeline
            from omni.timeline import TimelineEventType
        except Exception as exc:  # noqa: BLE001
            carb.log_warn(f"MountAssetRoot: timeline subscribe skipped: {exc}")
            return

        timeline = omni.timeline.get_timeline_interface()

        def _on_timeline(event):
            if event.type != int(TimelineEventType.STOP):
                return
            prim = self.prim
            if prim and prim.IsValid():
                self._pose_pending = True
                self._apply_pose_from_custom_data(prim)

        self._timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            _on_timeline
        )

    @staticmethod
    def _ee_selection(prim):
        sets = prim.GetVariantSets()
        if sets and sets.HasVariantSet("EE"):
            return sets.GetVariantSet("EE").GetVariantSelection()
        return None

    @staticmethod
    def _mount_child_list(stage, child_mounts, asset_root):
        for path, child_rel in child_mounts:
            child = stage.GetPrimAtPath(path) if stage is not None else None
            if child and child.IsValid():
                _mount_rel_on_prim(child, child_rel, asset_root)
            else:
                carb.log_error(f"MountAssetRoot: child {path} vanished before mount")

    def _collect_child_mounts(self, prim, asset_root=None):
        child_mounts: list[tuple[str, str]] = []
        stage = prim.GetStage()
        for child in Usd.PrimRange(prim):
            if child == prim or not child.IsValid():
                continue
            child_rel = child.GetCustomDataByKey(_REL_PATH_KEY)
            if child_rel:
                child_mounts.append((str(child.GetPath()), str(child_rel).strip()))
        for suffix in (
            "wrist_3_link/flange/tool0/EE",
            "flange/tool0/EE",
            "tool0/EE",
        ):
            path = f"{prim.GetPath()}/{suffix}"
            child = stage.GetPrimAtPath(path) if stage is not None else None
            if child and child.IsValid():
                child_rel = child.GetCustomDataByKey(_REL_PATH_KEY)
                if child_rel and all(path != existing for existing, _ in child_mounts):
                    child_mounts.append((path, str(child_rel).strip()))
        return child_mounts

    def on_update(self, current_time, delta_time):
        # When EE is switched after stage-open, the robot script does not
        # re-run on_init. Remount any newly composed library gripper.
        prim = self.prim
        if not prim or not prim.IsValid():
            return

        if getattr(self, "_pose_pending", False):
            self._apply_pose_from_custom_data(prim)

        ee = self._ee_selection(prim)
        if ee == getattr(self, "_last_ee", object()):
            return
        self._last_ee = ee
        if not ee or ee == "none":
            return
        try:
            asset_root = _resolve_asset_root()
        except Exception as exc:  # noqa: BLE001
            carb.log_error(
                f"MountAssetRoot: get_assets_root_path failed on update for {self.prim_path}: {exc}"
            )
            return
        if not asset_root:
            return
        child_mounts = self._collect_child_mounts(prim)
        if child_mounts:
            carb.log_info(
                f"MountAssetRoot: EE changed to {ee}, remounting {child_mounts}"
            )
            self._mount_child_list(prim.GetStage(), child_mounts, asset_root)
            self._pose_pending = True
            self._apply_pose_from_custom_data(prim)
