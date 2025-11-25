# Robot USDs for ROS2 Control

Robot USD model files for ROS2 Control simulation.

## Clone and Setup

```bash
# Clone the repository
git clone git@github.com:fiveages-sim/robot_usds.git
cd robot_usds

# Initialize and update submodules
git submodule update --init --recursive
```

## Models

- Gripper
    - ChangingTek_AG2F120S
    - ChangingTek_AG2F90_C
        - ChangingTek_AG2F90_C with soft pad (rigid body simulation)
    - ChangingTek_AG2F90_C_Soft
    - Inspire_EG2_4C2
    - Jodell_RG75
    - OmniPicker
    - Robotiq_85
- Manipulator
    - ARX5_agilex
    - DobotCR5
        - Dobot CR5 Dual Arm
    - Elite_EC66
    - Agilex Piper
    - rm65
- Humanoid
    - Agibot_G1
    - FiveAges_W1
- Mobile Base
    - Agilex_Tracer
- Mobile Manipulator
    - Agilex_Aloha_V1
    - Agilex_Aloha_V2
- Sensors
    - d405
    - d435
    - dabai
    - mid360

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
