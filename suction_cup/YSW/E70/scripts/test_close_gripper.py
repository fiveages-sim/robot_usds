"""Debug + close E70 SurfaceGripper.

Test setup: type=z4, flange=none (D6 poses assume flange=none / suction -Z).
Reload stage → Play → tips facing a massed rigid body → run this.
"""

import asyncio
import omni.kit.app
import omni.usd
from isaacsim.robot.surface_gripper.bindings._surface_gripper import (
    acquire_surface_gripper_interface,
    GripperStatus,
)


def _find_grippers(stage):
    out = []
    for prim in stage.Traverse():
        if prim.GetTypeName() == "IsaacSurfaceGripper":
            out.append(prim.GetPath().pathString)
    return out


def _dump_attachment_debug(stage, sg_path: str):
    sg = stage.GetPrimAtPath(sg_path)
    if not sg:
        print("[dbg] missing", sg_path)
        return
    max_d = sg.GetAttribute("isaac:maxGripDistance").Get()
    retry = sg.GetAttribute("isaac:retryInterval").Get()
    print(f"[dbg] maxGripDistance={max_d} retryInterval={retry}")
    rel = sg.GetRelationship("isaac:attachmentPoints")
    targets = rel.GetTargets() if rel else []
    for jp in targets:
        j = stage.GetPrimAtPath(jp)
        if not j:
            print("[dbg] missing joint", jp)
            continue
        axis = j.GetAttribute("isaac:forwardAxis").Get()
        clr = j.GetAttribute("isaac:clearanceOffset").Get()
        lp0 = j.GetAttribute("physics:localPos0").Get()
        lr0 = j.GetAttribute("physics:localRot0").Get()
        print(
            f"[dbg] joint {jp.name} forward={axis} clearance={clr} "
            f"localPos0={lp0} localRot0={lr0}"
        )


async def _main():
    stage = omni.usd.get_context().get_stage()
    paths = _find_grippers(stage)
    print("[find]", paths)
    if not paths:
        print("[ERROR] no IsaacSurfaceGripper — set type=z4, Stop→Play")
        return

    path = next((p for p in paths if "Right_Arm" in p or "right" in p.lower()), paths[0])
    print("[use]", path)
    _dump_attachment_debug(stage, path)

    sg = acquire_surface_gripper_interface()
    sg.set_write_to_usd(True)
    print("close", sg.close_gripper(path))

    for i in range(60):
        await omni.kit.app.get_app().next_update_async()
        st = sg.get_gripper_status(path)
        objs = sg.get_gripped_objects(path)
        if i % 10 == 0 or objs or st == GripperStatus.Closed:
            print(f"  t={i} status={st} gripped={objs}")
        if st == GripperStatus.Closed and objs:
            print("[OK] grasped")
            return
        if st == GripperStatus.Open and i > 5:
            print(
                "[FAIL] Open again, no grasp.\n"
                "  - Tips must face the object; gap < maxGripDistance\n"
                "  - Object: RigidBody + Collision + Mass\n"
                "  - flange=none with type=z4 (current D6 poses)\n"
                "  - Closing forever usually means ray miss (pose/orient)"
            )
            return

    st = sg.get_gripper_status(path)
    objs = sg.get_gripped_objects(path)
    print(f"[done] final status={st} gripped={objs}")
    if st == GripperStatus.Closing and not objs:
        print(
            "[HINT] stuck Closing = rays not hitting. Check tip normal vs cube, "
            "and that flange matches D6 poses (none)."
        )


asyncio.ensure_future(_main())
