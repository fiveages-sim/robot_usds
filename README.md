# Robot USDs for ROS2 Control

Robot USD model files for ROS2 Control simulation.



https://github.com/user-attachments/assets/5aea688f-bd91-41c7-8ce3-bc57e192f31e

## 1. Gallery

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
| <img src=".images/ai2_bot2.png" alt="Ai2 Bot2" width="300"> | <img src=".images/arx_lift2s.png" alt="ARX Lift2S" width="300"> | <img src=".images/galbot%20zero.png" alt="Galbot Zero" width="300"> |
| **Ai2 Bot2** | **ARX Lift2S** | **Galbot Zero** |
| <img src=".images/galbot%20s1.png" alt="Galbot S1" width="300"> | <img src=".images/galbot%20g1.png" alt="Galbot G1" width="300"> | |
| **Galbot S1** | **Galbot G1** | |

</div>

## 2. Clone and Setup

**Note:** Some robot assets are distributed as **Git submodules**. You must run the submodule init/update below so that each repository is checked out at the **path expected by this project** (see [§2.1](#21-git-submodules)). Otherwise those assets are missing or empty, and dependent scenes or USD references will not load correctly.

```bash
# Clone the repository
git clone git@github.com:fiveages-sim/robot_usds.git
cd robot_usds

# Initialize and update submodules
git submodule update --init --recursive
```

### 2.1 Git submodules

The following models are **Git submodules** (vendored repositories, checked in as gitlinks at fixed paths in this superproject). Paths are **relative to the `robot_usds` repository root**; init/update must populate **these exact locations** (not arbitrary folders) so that relative paths between USDs resolve. After a plain `git clone`, the submodule directories are empty or absent until you run the commands in §2.

| Path | Upstream repository | `branch` in `.gitmodules`* |
|------|---------------------|----------------------------|
| `humanoid/FiveAges_W1` | [fiveages-sim/fa-w1-usds](https://github.com/fiveages-sim/fa-w1-usds) | `main` |
| `humanoid/FiveAges_W2` | [fiveages-sim/fa-w2-usds](https://github.com/fiveages-sim/fa-w2-usds) | `main` |
| `humanoid/Agibot_G2` | [fiveages-sim/agibot-g2-usds](https://github.com/fiveages-sim/agibot-g2-usds) | — |
| `manipulators/Marvin` | [fiveages-sim/marvin-usds](https://github.com/fiveages-sim/marvin-usds) | `main` |
| `humanoid/Ubtech` | [fiveages-sim/ubtech-usds](https://github.com/fiveages-sim/ubtech-usds) | `main` |
| `humanoid/Galbot` | [fiveages-sim/galbot-usds](https://github.com/fiveages-sim/galbot-usds) | `main` |

\*A `branch` value is the remote branch recorded for that submodule. If empty, the superproject still pins a specific commit; use `git submodule update` to check out the recorded revision.

## 3. Models

### 3.1 Models by category

- **Gripper**
    - ChangingTek AG2F120S
    - ChangingTek AG2F90
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
    - ARX (`manipulators/ARX/`)
        - ARX R5 (`ARX_R5`)
        - ARX X5 (`ARX_X5`)
        - ARX5 Agilex (`ARX5_Agilex`)
        - ARX5 Gripper 2023 (`ARX5_Gripper_2023`)
        - ARX5 Gripper 2025 (`ARX5_Gripper_2025`)
    - DobotCR5
        - Dobot CR5 Dual Arm
    - Elite EC66
    - Galaxea
        - A1
        - A1X
        - A1Y
    - Agilex
        - Piper
    - Marvin (Tianji AI series)
    - Realman RM75
- **Humanoid**
    - Agibot G1
    - Agibot G2
    - Ai2 Bot2
    - ARX Lift (`humanoid/ARX_Lift`)
    - ARX X7S (`humanoid/ARX_X7S`)
    - Astribot S1
    - Dobot Atom
    - FiveAges W1
    - FiveAges W2
    - Galbot (`humanoid/Galbot` submodule)
        - Galbot One (`Galbot_One`)
        - Galbot Zero (`Galbot_Zero`)
        - Galbot S1 (`Galbot_S1`)
        - Galbot G1 (`Galbot_G1`)
    - Galaxea R1
        - Galaxea R1 Pro
    - Realman Aidal
    - Ubtech
- **Mobile Base**
    - Agilex Ranger Mini
    - Agilex Tracer
    - Agilex Tracer V2
- **Mobile Manipulator**
    - Agilex Aloha Spilt
    - Agilex Aloha V1
    - Agilex Aloha V2
    - ARX Lift2S (`mobile_manipulator/ARX_Lift2S`)
    - Galaxea R1 Lite
- **Sensors**
    - d405
    - d415
    - d435
    - dabai
    - mid360
    - oradar ms500
    - orbbec 336
    - orbbec 336L
    - orbbec dabai dw
    - usb camera 01
- **Stands**
    - Dual Stand1
    - Dual Stand2

## 4. Directory Structure

The core directory is `robots`, which contains the following subfolders and resources:

```bash
robots/
  grippers/           # Gripper models and their configurations
  dexhands/           # Dexterous hand models and their configurations
  manipulators/       # Manipulator models, environment samples, and configurations
  humanoid/          # Humanoid robot models and configurations
  mobile_base/        # Mobile base models and configurations
  mobile_manipulator/ # Mobile manipulator models and configurations
  sensors/            # Sensor models
  stands/             # Stand / fixture models
  README.md
  LICENSE
```

Some scenes under `manipulators/*/envs/` depend on external environment assets (textures, shared assets, etc.).

## 5. Using Environment Assets

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
