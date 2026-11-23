# LimX DACH TRON2B

Open `DACH_TRON2B.usda` to inspect the fixed-base robot asset. Its relative
payloads contain the geometry and physics. The default physics variant is PhysX.

Source: `dach_tron2b_description` from the ROS robot-descriptions workspace,
expanded with `isaac:=true` and converted using the Isaac Sim 6.2 URDF
importer. `payloads/glb_visuals.usdc` contains the colored visuals converted
from the same description package's GLB meshes. The visuals follow the
PhysX links and the existing STL-derived collision shapes are retained.
Run FaSim-Isaac's `tools/tron2b-isaac/run.sh` for the ROS 2 bridge and ground.
