# SPDX-FileCopyrightText: Copyright (c) 2026 FiveAges
# SPDX-License-Identifier: Apache-2.0
"""Mount an Isaac asset-root-relative USD onto this prim when the stage opens.

Reads ``customData["fasim_asset_root_rel_path"]``, resolves it with
``get_assets_root_path()`` (honors ``ISAACSIM_ASSET_REGION_PROFILE`` /
``ISAACSIM_ASSET_ROOT``), and authors that payload on ``Robotiq_2F_85.usda`` itself (not the session
layer). ``payloads/Joints/ros2_names.usda`` is a sublayer of that file, so
its joint rename and mimic retarget stay stronger than the official asset.

Mount position is not this script's job. Offsets belong on the variant payload,
the same way AG2F90 Flange and CR5 Sensor=KWR75B author ``xformOp:translate``.

Do not hardcode S3 URLs here.
"""

from __future__ import annotations

import carb
from omni.behavior.scripting.core import BehaviorScript
from pxr import Sdf


_REL_PATH_KEY = "fasim_asset_root_rel_path"
_DEFAULT_REL_PATH = "Isaac/Robots_Multiphysics/Robotiq/2F-85/Robotiq_2F_85.usda"


def _join_asset_root(root: str, rel: str) -> str:
    return f"{root.rstrip('/')}/{rel.lstrip('/')}"


def _is_official_mount(path: str, rel: str, full: str) -> bool:
    if path == full:
        return True
    rel_norm = rel.lstrip("/")
    normalized = path.replace("\\", "/").rstrip("/")
    if not normalized.endswith("/" + rel_norm) and normalized != rel_norm:
        return False
    return "://" in path or normalized.startswith("/") or normalized.startswith("omniverse:")


def _gripper_layer(prim):
    """Layer that defines this gripper, so its sublayers stay stronger than the official payload."""
    suffix = "/robots/grippers/Robotiq/2F-85/Robotiq_2F_85.usda"
    for spec in prim.GetPrimStack():
        ident = spec.layer.identifier.replace("\\", "/")
        if ident.endswith(suffix):
            return spec.layer
    return None


def _payload_items(sdf_prim):
    op = sdf_prim.payloadList
    return list(op.prependedItems) + list(op.appendedItems) + list(op.explicitItems)


def _mount_rel_on_prim(prim, rel: str, asset_root: str) -> None:
    if not rel:
        carb.log_error(f"MountAssetRoot: empty {_REL_PATH_KEY} on {prim.GetPath()}")
        return
    full = _join_asset_root(asset_root, rel)
    layer = _gripper_layer(prim)
    sdf_prim = layer.GetPrimAtPath("/Robotiq_2F_85") if layer is not None else None
    if sdf_prim is None or not layer.permissionToEdit:
        carb.log_error(
            f"MountAssetRoot: cannot mount {full} under Robotiq_2F_85.usda "
            f"for {prim.GetPath()}"
        )
        return

    def _keep(items):
        return [item for item in items if not _is_official_mount(str(item.assetPath), rel, full)]

    already = any(str(item.assetPath) == full for item in _payload_items(sdf_prim))
    if not already:
        # Appended on this layer: weaker than payloads/Joints/ros2_names.usda,
        # which renames finger_joint and retargets the PhysX mimics.
        sdf_prim.payloadList.prependedItems = _keep(sdf_prim.payloadList.prependedItems)
        sdf_prim.payloadList.appendedItems = _keep(sdf_prim.payloadList.appendedItems) + [
            Sdf.Payload(full)
        ]
        carb.log_info(f"MountAssetRoot: mounted {full} under Robotiq_2F_85.usda")
    else:
        carb.log_info(f"MountAssetRoot: already mounted {full} under Robotiq_2F_85.usda")


class MountAssetRoot(BehaviorScript):
    def on_init(self):
        prim = self.prim
        if not prim or not prim.IsValid():
            carb.log_error(f"MountAssetRoot: invalid prim at {self.prim_path}")
            return

        rel = (prim.GetCustomDataByKey(_REL_PATH_KEY) or _DEFAULT_REL_PATH).strip()
        if not rel:
            carb.log_error(f"MountAssetRoot: empty {_REL_PATH_KEY} on {self.prim_path}")
            return

        try:
            from isaacsim.storage.native import get_assets_root_path

            root = get_assets_root_path()
        except Exception as exc:  # noqa: BLE001
            carb.log_error(
                f"MountAssetRoot: get_assets_root_path failed for {self.prim_path}: {exc}"
            )
            return

        if not root:
            carb.log_error(f"MountAssetRoot: empty asset root for {self.prim_path}")
            return

        _mount_rel_on_prim(prim, rel, root)
