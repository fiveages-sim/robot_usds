# Robot USDs for ROS2 Control

Robot USD model files for ROS2 Control simulation.



https://github.com/user-attachments/assets/5aea688f-bd91-41c7-8ce3-bc57e192f31e

## Gallery

<div align="center">

| | | |
|:---:|:---:|:---:|
| <img src=".images/agibot_g1.png" alt="Agibot G1" width="300"/> | <img src=".images/agilex_aloha_split.png" alt="Agilex Aloha Split" width="300"/> | <img src=".images/agilex_aloha_v1.png" alt="Agilex Aloha V1" width="300"/> |
| **Agibot G1** | **Agilex Aloha Split** | **Agilex Aloha V1** |
| <img src=".images/agilex_aloha_v2.png" alt="Agilex Aloha V2" width="300"/> | <img src=".images/galaxea_r1_lite.png" alt="Galaxea R1 Lite" width="300"/> | <img src=".images/galaxea_r1.png" alt="Galaxea R1" width="300"/> |
| **Agilex Aloha V2** | **Galaxea R1 Lite** | **Galaxea R1** |
| <img src=".images/galaxea_r1_pro.png" alt="Galaxea R1 Pro" width="300"/> | | |
| **Galaxea R1 Pro** | | |

</div>

## Clone and Setup

```bash
# Clone the repository
git clone git@github.com:fiveages-sim/robot_usds.git
cd robot_usds

# Initialize and update submodules
git submodule update --init --recursive
```

## Models

- **Gripper**
    - ChangingTek_AG2F120S
    - ChangingTek_AG2F90_C
        - ChangingTek_AG2F90_C with soft pad (rigid body simulation)
    - ChangingTek_AG2F90_C_Soft
    - Galaxea_G1
    - Inspire_EG2_4C2
    - Jodell_RG75
    - OmniPicker
    - Robotiq_85
- **Manipulator**
    - ARX5_agilex
    - DobotCR5
        - Dobot CR5 Dual Arm
    - Elite_EC66
    - Galaxea
        - A1
        - A1X
        - A1Y
    - Piper
    - rm65
- **Humanoid**
    - Agibot_G1
    - Agibot_G2
    - FiveAges_W1
    - FiveAges_W2
    - Galaxea_R1
        - Galaxea_R1_Pro
- **Mobile Base**
    - Agilex_Ranger_Mini
    - Agilex_Tracer
    - Agilex_Tracer_V2
- **Mobile Manipulator**
    - Agilex_Aloha_Spilt
    - Agilex_Aloha_V1
    - Agilex_Aloha_V2
    - Galaxea_R1_Lite
- **Sensors**
    - d405
    - d435
    - dabai
    - mid360
    - orbbec_336
    - orbbec_336L

## Directory Structure

The core directory is `robots`, which contains the following subfolders and resources:

```bash
robots/
  grippers/           # Gripper models and their configurations
  manipulators/       # Manipulator models, environment samples, and configurations
  humannoid/          # Humanoid robot models and configurations
  mobile_base/        # Mobile base models and configurations
  mobile_manipulator/ # Mobile manipulator models and configurations
  sensors/            # Sensor models
  README.md
  LICENSE
```

Some scenes under `manipulators/*/envs/` depend on external environment assets (textures, shared assets, etc.).

## Using Environment Assets

To use environment assets, create an `environment` folder at the same level as `robots`, then clone `fiveages_env` inside it:

```bash
# Go to the parent directory of robots (adjust the path as needed)
cd /home/fiveages/Documents/usd

mkdir -p environment
cd environment

# Clone the environment assets repository
git clone git@github.com:fiveages-sim/fiveages-env-usds.git fiveages_env
```

After cloning, your directory layout should look like:

```bash
/home/fiveages/Documents/usd/
  robots/
  environment/
    fiveages_env/
```

With this layout, scenes that depend on environment assets can correctly reference content from `environment/fiveages_env`.
