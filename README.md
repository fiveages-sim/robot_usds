# Robot USDs for ROS2 Control

Robot USD model files for ROS2 Control simulation.



https://github.com/user-attachments/assets/5aea688f-bd91-41c7-8ce3-bc57e192f31e

## Gallery

<div align="center">

| | | |
|:---:|:---:|:---:|
| <img src=".images/agibot_g1.png" alt="Agibot G1" width="300"> | <img src=".images/agilex_aloha_split.png" alt="Agilex Aloha Split" width="300"> | <img src=".images/agilex_aloha_v1.png" alt="Agilex Aloha V1" width="300"> |
| **Agibot G1** | **Agilex Aloha Split** | **Agilex Aloha V1** |
| <img src=".images/agilex_aloha_v2.png" alt="Agilex Aloha V2" width="300"> | <img src=".images/arx_lift.png" alt="ARX Lift" width="300"> | <img src=".images/arx_x7s.png" alt="ARX X7S" width="300"> |
| **Agilex Aloha V2** | **ARX Lift** | **ARX X7S** |
| <img src=".images/astribot_s1.png" alt="Astribot S1" width="300"> | <img src=".images/galaxea_r1_lite.png" alt="Galaxea R1 Lite" width="300"> | <img src=".images/galaxea_r1.png" alt="Galaxea R1" width="300"> |
| **Astribot S1** | **Galaxea R1 Lite** | **Galaxea R1** |
| <img src=".images/galaxea_r1_pro.png" alt="Galaxea R1 Pro" width="300"> | <img src=".images/galbot%20one.png" alt="Galbot One" width="300"> | <img src=".images/realman%20aidal.png" alt="Realman Aidal" width="300"> |
| **Galaxea R1 Pro** | **Galbot One** | **Realman Aidal** |

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
    - ChangingTek AG2F120S
    - ChangingTek AG2F90-C
    - Galaxea G1
    - Inspire EG2 4C2
    - Jodell RG75
    - OmniPicker
    - Robotiq 85
- **Dexterous Hand**
    - BrainCo Revo1
    - BrainCo Revo2
    - LinkerHand o6
    - LinkerHand o7
- **Manipulator**
    - ARX
        - R5
        - X5
    - ARX5 agilex
    - DobotCR5
        - Dobot CR5 Dual Arm
    - Elite EC66
    - Galaxea
        - A1
        - A1X
        - A1Y
    - Piper
    - Realman RM75
- **Humanoid**
    - Agibot G1
    - Agibot G2
    - ARX Lift
    - ARX X7S
    - Astribot S1
    - FiveAges W1
    - FiveAges W2
    - Galbot One
    - Galaxea R1
        - Galaxea R1 Pro
    - Realman Aidal
- **Mobile Base**
    - Agilex Ranger Mini
    - Agilex Tracer
    - Agilex Tracer V2
- **Mobile Manipulator**
    - Agilex Aloha Spilt
    - Agilex Aloha V1
    - Agilex Aloha V2
    - Galaxea R1 Lite
- **Sensors**
    - d405
    - d435
    - dabai
    - mid360
    - orbbec 336
    - orbbec 336L

## Directory Structure

The core directory is `robots`, which contains the following subfolders and resources:

```bash
robots/
  grippers/           # Gripper models and their configurations
  dexhands/           # Dexterous hand models and their configurations
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
