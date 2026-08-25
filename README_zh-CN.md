# 面向 ROS2 Control 的机器人 USD 资源

机器人 USD 模型文件，用于 ROS2 Control 仿真。


![teaser.png](.images/teaser.png)

## 1. 照片墙

<div align="center">

| | | |
|:---:|:---:|:---:|
| <img src=".images/agibot_g1.png" alt="智元 G1" width="300"> | <img src=".images/agilex_aloha_split.png" alt="松灵 Aloha Split" width="300"> | <img src=".images/agilex_aloha_v2.png" alt="松灵 Aloha V2" width="300"> |
| **智元 G1** | **松灵 Aloha Split** | **松灵 Aloha V2** |
| <img src=".images/arx_lift.png" alt="方舟无限 Lift" width="300"> | <img src=".images/arx_x7s.png" alt="方舟无限 X7S" width="300"> | <img src=".images/arx_lift2s.png" alt="方舟无限 Lift 2S" width="300"> |
| **方舟无限 Lift** | **方舟无限 X7S** | **方舟无限 Lift 2S** |
| <img src=".images/astribot_s1.png" alt="星尘智能 S1" width="300"> | <img src=".images/galaxea_r1_lite.png" alt="星海图 R1 Lite" width="300"> | <img src=".images/galaxea_r1.png" alt="星海图 R1" width="300"> |
| **星尘智能 S1** | **星海图 R1 Lite** | **星海图 R1** |
| <img src=".images/galaxea_r1_pro.png" alt="星海图 R1 Pro" width="300"> | <img src=".images/galbot%20one.png" alt="银河通用 Galbot One" width="300"> | <img src=".images/realman%20aidal.png" alt="睿尔曼 Aidal" width="300"> |
| **星海图 R1 Pro** | **银河通用 Galbot One** | **睿尔曼 Aidal** |
| <img src=".images/ai2_bot2.png" alt="智平方 Bot2" width="300"> | <img src=".images/galbot%20zero.png" alt="银河通用 Galbot Zero" width="300"> | |
| **智平方 Bot2** | **银河通用 Galbot Zero** | |
| <img src=".images/galbot%20s1.png" alt="银河通用 Galbot S1" width="300"> | <img src=".images/galbot%20g1.png" alt="银河通用 Galbot G1" width="300"> | |
| **银河通用 S1** | **银河通用 G1** | |

</div>

## 2. 克隆与初始化

**说明：** 部分机器人资产以 **Git 子模块** 管理，**必须**按本仓库约定的路径将子模块初始化并拉取到正确位置（见下节命令与 [§2.1](#21-子模块git) 中的路径表），相关 USD 与层引用才能被正常解析；只克隆父仓库、不执行子模块更新时，这些目录会为空或不存在，相关场景无法正常使用。

```bash
# 克隆仓库
git clone git@github.com:fiveages-sim/robot_usds.git
cd robot_usds

# 初始化并更新子模块
git submodule update --init --recursive
```

### 2.1 子模块（Git）

以下目录为 **Git 子模块**（在父仓库中通过子模块 commit 与固定路径挂载）。**路径均相对于本仓库 `robot_usds` 根目录，且需落在表中位置**（子模块必须检出到这些路径，而不是任意副本），否则与主仓库内其他 USD 的相对引用会失效。仅在上面的「初始化并更新子模块」执行完成后，这些目录中才会有完整内容。

| 路径 | 上游仓库 | `.gitmodules` 中的 `branch`* |
|------|----------|------------------------------|
| `humanoid/FiveAges/Gen1` | [fiveages-sim/fiveages-gen1-robot-usds](https://github.com/fiveages-sim/fiveages-gen1-robot-usds) | `main` |
| `humanoid/FiveAges/Gen2` | [fiveages-sim/fiveages-gen2-robot-usds](https://github.com/fiveages-sim/fiveages-gen2-robot-usds) | `main` |
| `humanoid/FiveAges/Gen3` | [fiveages-sim/fiveages-gen3-robot-usds](https://github.com/fiveages-sim/fiveages-gen3-robot-usds) | `main` |
| `humanoid/Agibot_G2` | [fiveages-sim/agibot-g2-usds](https://github.com/fiveages-sim/agibot-g2-usds) | — |
| `humanoid/Ubtech` | [fiveages-sim/ubtech-usds](https://github.com/fiveages-sim/ubtech-usds) | `main` |
| `humanoid/Galbot` | [fiveages-sim/galbot-usds](https://github.com/fiveages-sim/galbot-usds) | `main` |

\*`branch` 为子模块配置里记录的远程分支，便于 `git submodule update --remote` 等；未填写时，父仓库仍通过固定 commit 锁版本，使用 `git submodule update` 会检出所记录的该提交。

## 3. 模型

### 3.1 中文简称与英文标识对照

展示名尽量采用 **「中文简称 + 型号」**（与 **智元 G1** 同类）；下表给出与仓库目录、USD 中常用 **英文标识** 的对应关系。

| 中文简称 | 英文品牌 / 常用标识 |
|:---|:---|
| 智元 | Agibot、OmniPicker |
| 松灵 | Agilex、Piper |
| 方舟无限 | ARX |
| 星尘智能 | Astribot |
| 星海图 | Galaxea |
| 银河通用 | Galbot |
| 睿尔曼 | Realman |
| 越疆 | Dobot |
| 艾利特 | Elite |
| 因时 | Inspire |
| 强脑 | BrainCo |
| 灵心巧手 | LinkerHand |
| 知行 | ChangingTek |
| 钧舵 | Jodell |
| 智平方 | Ai2 |
| 中科第五纪 | FiveAges |
| 优必选 | Ubtech |
| 天机智能 | Tianji、Marvin（系列） |
| （保留英文） | Robotiq |

### 3.2 按类别列出

- **Gripper（夹爪）** — `grippers/`
    - 知行（`ChangingTek/`）：AG2F120S、AG2F90
    - 因时 EG2 4C2（`Inspire_EG2_4C2`）
    - 钧舵（`Jodell/`）：RG75、ERG32
    - 智元 OmniPicker
    - Robotiq 85（`Robotiq_85`）
- **Dexterous Hand（灵巧手）** — `dexhands/`
    - 强脑 Revo1 / Revo2（`BrainCo_Revo1`、`BrainCo_Revo2`）
    - 灵心巧手 o6（`o6`）、o7（`LinkerHand_o7`）、`LinkerHands`
- **Manipulator（机械臂）** — `manipulators/`（品牌目录 → 短产品名）
    - 方舟无限（`manipulators/ARX/`）：`X5`、`R5`、`Gripper_2023`、`Gripper_2025`
    - 星海图（`manipulators/Galaxea/`）：`A1` / `A1X` / `A1Y` / `A1Z`、`G1` / `G1Z`
    - 松灵（`manipulators/Agilex/`）：Piper
    - 越疆（`manipulators/Dobot/`）：CR5、`CR5_Fa_Station`
    - 艾利特（`manipulators/Elite/`）：EC66
    - 法奥（`manipulators/Fairino/`）：ART7
    - 天机智能（`manipulators/Tianji/`）：`M6_CCS`、`M6_Fa_Station`、`M20S_CCS`
    - 珞石（`manipulators/Rokae/`）：`AR5_CCS_V1` / `AR5_CCS_V2`、`AR5_SRS`
    - 睿尔曼 RM75（`Realman_RM75`）
    - Panthera HT（`Panthera_HT`）
- **Humanoid（人形机器人）** — `humanoid/`
    - 智元 G1 / G2（`Agibot_G1`、`Agibot_G2` 子模块）
    - 智平方 Bot2（`Ai2_Bot2`）
    - 星尘智能 S1（`Astribot_S1`）
    - 越疆 Atom（`Dobot_Atom`）
    - 中科第五纪（`humanoid/FiveAges/`）：Gen1 / Gen2 / Gen3（W1 / W2 / WCE3，子模块）
    - 星海图（`humanoid/Galaxea/`）
        - R1（`R1`，含 Robot 变体 `R1_Pro`）
        - R1 Lite（`R1_Lite`）
    - 银河通用 Galbot（`humanoid/Galbot` 子模块）：One / Zero / S1 / G1
    - 睿尔曼 Aidal（`Realman_AIDAL`）
    - SpiritAI Moz1（`SpiritAI_Moz1`）
    - 优必选（`Ubtech` 子模块）
- **Mobile Base（移动底盘）** — `mobile_base/`
    - 松灵 Ranger Mini（`Agilex_Ranger_Mini`）
    - 松灵 Tracer（`Agilex_Tracer`）、Tracer V1（`Agilex/Tracer_V1`）、Tracer V2（`Agilex_Tracer_V2`）
    - 灵猴（`Linkhou/`）：Q1、S2_V1、S2_V2
- **Mobile Manipulator（移动机械臂）** — `mobile_manipulator/`
    - 松灵 Aloha Split（`Agilex_Aloha_Spilt`）、Aloha V2（`Agilex_Aloha_V2`）
    - 松灵 Cobot Magic V1（`Agilex/Cobot Magic V1`）
    - 方舟无限（`mobile_manipulator/ARX/`）
        - Lift（`Lift`）
        - Lift 2S（`Lift 2S`）
        - X7S（`X7S`）
        - AC One Base（`AC_One_Base`）
- **Components（共享组件）** — `components/`
    - Angellun_8 / Angellun_10、omnia_150、fixed_ee
- **Sensors（传感器）** — `sensors/`
    - RealSense d405 / d415 / d435
    - dabai、mid360、oradar_ms500
    - orbbec 305 / 336 / 336L / dabai_dw（及 `orbbec/`）
    - usb_camera_01 / usb_camera_02、linkhou_ds51、robosense_airy、ultrasonic_02 等

## 4. 文件结构

项目核心目录为 `robots`。品牌资产采用 **品牌目录 + 短产品名**（与 `manipulators/ARX/X5`、`humanoid/Galaxea/R1` 一致）：

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

`*/env/` 下部分场景依赖外部环境资源（见第 5 节）。

## 5. 使用环境内容

如需使用环境的内容，请在与 `robots` 同级的位置新建一个 `environment` 文件夹，并在该文件夹内克隆 `fiveages_env`：

```bash
# 进入 robots 的上级目录（示例路径按需调整）
cd /home/fiveages/Documents/usd

mkdir -p environment
cd environment

# 克隆环境资源仓库
git clone git@github.com:fiveages-sim/fiveages-env-usds.git fiveages_env
```

完成后目录结构应类似：

```bash
/home/fiveages/Documents/usd/
  robots/
  environment/
    fiveages_env/
```

这样，依赖环境资源的场景即可正常引用 `environment/fiveages_env` 中的内容。
