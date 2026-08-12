#!/usr/bin/env python3
"""Measure Ai2_Bot2 horizontal wrapping radius from its USD (default/arms-tucked pose).

Run inside the Isaac Sim python env (which ships the `pxr` USD API), from this dir:

    /isaac-sim/python.sh measure_footprint_radius.py
    # or, if pxr is on PATH:
    python3 measure_footprint_radius.py [path/to/Ai2_Bot2.usda]

It computes the world-space axis-aligned bounding box of the whole robot
(includes arms, shoulders, every referenced mesh) and reports:

  - inscribed_radius  = min horizontal half-axis  (nav2: "always-collide" bound)
  - circumscribed_r   = farthest horizontal vertex = min enclosing-cylinder radius
                        (this is what you want: "no rotation can ever hit")

All numbers are printed BOTH pre-scale (raw USD) and after the model_params
`scale: 0.8` that Arena applies at launch. Use the *after-scale* circumscribed
value (+ margin) as the physical wrapping radius.

Note: model_params `robot_radius` is a PRE-scale value (Arena multiplies by 0.8
at launch), so if you switch to a circle model, put  radius_physical / 0.8  there.
"""
import math
import sys

try:
    from pxr import Usd, UsdGeom, Gf
except ImportError:
    sys.exit("pxr (USD Python API) not found. Run with Isaac's python: "
             "/isaac-sim/python.sh measure_footprint_radius.py")

SCALE = 0.8  # model_params.yaml Ai2_Bot2 scale
ROBOT_PRIM = "/Ai2_Bot2"

usd_path = sys.argv[1] if len(sys.argv) > 1 else "Ai2_Bot2.usda"
stage = Usd.Stage.Open(usd_path)
if stage is None:
    sys.exit(f"could not open {usd_path}")

prim = stage.GetPrimAtPath(ROBOT_PRIM)
if not prim or not prim.IsValid():
    # fall back to default/root prim
    prim = stage.GetDefaultPrim() or stage.GetPseudoRoot()
    print(f"[warn] {ROBOT_PRIM} not found, using {prim.GetPath()}")

cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                          ["default", "render", "proxy", "guide"])
bound = cache.ComputeWorldBound(prim)
rng = bound.ComputeAlignedRange()
mn, mx = rng.GetMin(), rng.GetMax()

# horizontal (XY) extents relative to robot origin (0,0)
half_x = max(abs(mn[0]), abs(mx[0]))
half_y = max(abs(mn[1]), abs(mx[1]))
inscribed = min(half_x, half_y)          # nearest edge
circumscribed = math.hypot(half_x, half_y)  # farthest corner

def line(label, v):
    print(f"  {label:28s} pre-scale={v:.4f} m   after-scale(x{SCALE})={v*SCALE:.4f} m")

print(f"\nUSD: {usd_path}   prim: {prim.GetPath()}")
print(f"AABB min = ({mn[0]:.4f}, {mn[1]:.4f}, {mn[2]:.4f})")
print(f"AABB max = ({mx[0]:.4f}, {mx[1]:.4f}, {mx[2]:.4f})")
print()
line("half_x (fwd/back)", half_x)
line("half_y (left/right)", half_y)
line("inscribed_radius (min edge)", inscribed)
line("circumscribed_radius (corner)", circumscribed)

phys_circ = circumscribed * SCALE
print("\n--- suggested nav2 / model_params values ---")
print(f"  physical wrapping radius (after scale) = {phys_circ:.4f} m")
print(f"  circle-model robot_radius (PRE-scale, put in model_params) "
      f"= {circumscribed:.4f} m")
print(f"  recommended inflation_radius >= {phys_circ:.2f} + margin "
      f"(e.g. {phys_circ+0.10:.2f} m with 0.10 m margin)")
