# SPDX-FileCopyrightText: Copyright (c) 2026 FiveAges
# SPDX-License-Identifier: Apache-2.0
"""Mount an Isaac asset-root-relative USD onto this prim when the stage opens.

Reads ``customData["fasim_asset_root_rel_path"]``, resolves it with
``get_assets_root_path()`` (honors ``ISAACSIM_ASSET_REGION_PROFILE`` /
``ISAACSIM_ASSET_ROOT``), and authors a payload on the session edit target.

Do not hardcode S3 URLs here.
"""

from __future__ import annotations

import carb
from omni.behavior.scripting.core import BehaviorScript
from pxr import Sdf


_REL_PATH_KEY = "fasim_asset_root_rel_path"
_DEFAULT_REL_PATH = "Isaac/Robots_Multiphysics/Robotiq/2F-85/Robotiq_2F_85.usda"


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
    if path == full:
        return True
    rel_norm = rel.lstrip("/")
    normalized = path.replace("\\", "/").rstrip("/")
    if not normalized.endswith("/" + rel_norm) and normalized != rel_norm:
        return False
    return "://" in path or normalized.startswith("/") or normalized.startswith("omniverse:")


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
