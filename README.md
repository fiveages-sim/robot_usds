# Robot USDs for ROS2 Control

Robot USD model files for ROS2 Control simulation.

![teaser.png](.images/teaser.png)

## 1. Gallery

<div align="center">

| | | |
|:---:|:---:|:---:|
| <img src=".images/agibot_g1.png" alt="Agibot G1" width="300"> | <img src=".images/agilex_aloha_split.png" alt="Agilex Aloha Split" width="300"> | <img src=".images/agilex_aloha_v2.png" alt="Agilex Aloha V2" width="300"> |
| **Agibot G1** | **Agilex Aloha Split** | **Agilex Aloha V2** |
| <img src=".images/arx_lift.png" alt="ARX Lift" width="300"> | <img src=".images/arx_x7s.png" alt="ARX X7S" width="300"> | <img src=".images/arx_lift2s.png" alt="ARX Lift 2S" width="300"> |
| **ARX Lift** | **ARX X7S** | **ARX Lift 2S** |
| <img src=".images/astribot_s1.png" alt="Astribot S1" width="300"> | <img src=".images/galaxea_r1_lite.png" alt="Galaxea R1 Lite" width="300"> | <img src=".images/galaxea_r1.png" alt="Galaxea R1" width="300"> |
| **Astribot S1** | **Galaxea R1 Lite** | **Galaxea R1** |
| <img src=".images/galaxea_r1_pro.png" alt="Galaxea R1 Pro" width="300"> | <img src=".images/galbot%20one.png" alt="Galbot One" width="300"> | <img src=".images/realman%20aidal.png" alt="Realman Aidal" width="300"> |
| **Galaxea R1 Pro** | **Galbot One** | **Realman Aidal** |
| <img src=".images/ai2_bot2.png" alt="Ai2 Bot2" width="300"> | <img src=".images/galbot%20zero.png" alt="Galbot Zero" width="300"> | |
| **Ai2 Bot2** | **Galbot Zero** | |
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
| `humanoid/FiveAges/Gen1` | [fiveages-sim/fiveages-gen1-robot-usds](https://github.com/fiveages-sim/fiveages-gen1-robot-usds) | `main` |
| `humanoid/FiveAges/Gen2` | [fiveages-sim/fiveages-gen2-robot-usds](https://github.com/fiveages-sim/fiveages-gen2-robot-usds) | `main` |
| `humanoid/FiveAges/Gen3` | [fiveages-sim/fiveages-gen3-robot-usds](https://github.com/fiveages-sim/fiveages-gen3-robot-usds) | `main` |
| `humanoid/Agibot_G2` | [fiveages-sim/agibot-g2-usds](https://github.com/fiveages-sim/agibot-g2-usds) | — |
| `humanoid/Ubtech` | [fiveages-sim/ubtech-usds](https://github.com/fiveages-sim/ubtech-usds) | `main` |
| `humanoid/Galbot` | [fiveages-sim/galbot-usds](https://github.com/fiveages-sim/galbot-usds) | `main` |

\*A `branch` value is the remote branch recorded for that submodule. If empty, the superproject still pins a specific commit; use `git submodule update` to check out the recorded revision.

## 3. Models

### 3.1 Models by category

- **Gripper** — under `grippers/`
    - ChangingTek (`ChangingTek/`)
        - AG2F120S
        - AG2F90
    - Inspire EG2 4C2 (`Inspire_EG2_4C2`)
    - Jodell (`Jodell/`)
        - RG75
        - ERG32
    - OmniPicker
    - Robotiq 85 (`Robotiq_85`)
- **Dexterous Hand** — under `dexhands/`
    - BrainCo Revo1 (`BrainCo_Revo1`)
    - BrainCo Revo2 (`BrainCo_Revo2`)
    - LinkerHand o6 (`o6`)
    - LinkerHand o7 (`LinkerHand_o7`)
    - LinkerHands (`LinkerHands`)
- **Manipulator** — under `manipulators/` (brand folder → product short name)
    - ARX (`manipulators/ARX/`)
        - X5
        - R5
        - Gripper 2023 (`Gripper_2023`)
        - Gripper 2025 (`Gripper_2025`)
    - Galaxea (`manipulators/Galaxea/`)
        - A1 / A1X / A1Y / A1Z
        - G1 / G1Z
    - Agilex (`manipulators/Agilex/`)
        - Piper
    - Dobot (`manipulators/Dobot/`)
        - CR5
        - CR5 Fa Station (`CR5_Fa_Station`)
    - Elite (`manipulators/Elite/`)
        - EC66
    - Fairino (`manipulators/Fairino/`)
        - ART7
    - Tianji (`manipulators/Tianji/`)
        - M6 CCS (`M6_CCS`)
        - M6 Fa Station (`M6_Fa_Station`)
        - M20S CCS (`M20S_CCS`)
    - Rokae (`manipulators/Rokae/`)
        - AR5 CCS V1 / V2 (`AR5_CCS_V1`, `AR5_CCS_V2`)
        - AR5 SRS (`AR5_SRS`)
    - Realman RM75 (`Realman_RM75`)
    - Panthera HT (`Panthera_HT`)
- **Humanoid** — under `humanoid/`
    - Agibot G1 (`Agibot_G1`)
    - Agibot G2 (`Agibot_G2` submodule)
    - Ai2 Bot2 (`Ai2_Bot2`)
    - Astribot S1 (`Astribot_S1`)
    - Dobot Atom (`Dobot_Atom`)
    - FiveAges (`humanoid/FiveAges/`)
        - W1 / Gen1 (`Gen1` submodule)
        - W2 / Gen2 (`Gen2` submodule)
        - WCE3 / Gen3 (`Gen3` submodule)
    - Galaxea (`humanoid/Galaxea/`)
        - R1 (`R1`) — includes R1 Pro (Robot variant `R1_Pro`)
        - R1 Lite (`R1_Lite`)
    - Galbot (`humanoid/Galbot` submodule)
        - Galbot One / Zero / S1 / G1
    - Realman Aidal (`Realman_AIDAL`)
    - SpiritAI Moz1 (`SpiritAI_Moz1`)
    - Ubtech (`Ubtech` submodule)
- **Mobile Base** — under `mobile_base/`
    - Agilex Ranger Mini (`Agilex_Ranger_Mini`)
    - Agilex Tracer (`Agilex_Tracer`)
    - Agilex Tracer V1 (`Agilex/Tracer_V1`)
    - Agilex Tracer V2 (`Agilex_Tracer_V2`)
    - Linkhou (`Linkhou/`) — Q1, S2_V1, S2_V2
- **Mobile Manipulator** — under `mobile_manipulator/`
    - Agilex Aloha Split (`Agilex_Aloha_Spilt`)
    - Agilex Aloha V2 (`Agilex_Aloha_V2`)
    - Agilex Cobot Magic V1 (`Agilex/Cobot Magic V1`)
    - ARX (`mobile_manipulator/ARX/`)
        - Lift (`Lift`)
        - Lift 2S (`Lift 2S`)
        - X7S (`X7S`)
        - AC One Base (`AC_One_Base`)
- **Components** — under `components/` (shared wheels / fixtures)
    - Angellun_8 / Angellun_10
    - omnia_150
    - fixed_ee
- **Sensors** — under `sensors/`
    - RealSense d405 / d415 / d435
    - dabai, mid360, oradar_ms500
    - orbbec 305 / 336 / 336L / dabai_dw (+ `orbbec/` extras)
    - usb_camera_01 / usb_camera_02
    - linkhou_ds51, robosense_airy, ultrasonic_02
    - 6Dof F&T Sensor, sick, sensing

## 4. Directory Structure

The core directory is `robots`. Brand-owned product trees use **short product names** under a brand folder (same pattern as `manipulators/ARX/X5`, `humanoid/Galaxea/R1`):

```bash
robots/
  grippers/
  dexhands/
  manipulators/
    ARX/{X5,R5,Gripper_2023,Gripper_2025}/
    Galaxea/{A1,A1X,A1Y,A1Z,G1,G1Z}/
    Agilex/Piper/
    Dobot/ … Elite/ … Fairino/ … Tianji/ … Rokae/ …
  humanoid/
    FiveAges/{Gen1,Gen2,Gen3}/
    Galaxea/{R1,R1_Lite}/
    Galbot/ … Agibot_G1/ … Agibot_G2/ …
  mobile_base/
  mobile_manipulator/
    ARX/{Lift,Lift 2S,X7S,AC_One_Base}/
    Agilex/Cobot Magic V1/
    Agilex_Aloha_Spilt/  Agilex_Aloha_V2/
  components/
  sensors/
  README.md
  LICENSE
```

Some scenes under `*/env/` depend on external environment assets (see §5).

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