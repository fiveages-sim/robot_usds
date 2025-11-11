# 面向 ROS2 Control 的机器人 USD 资源

机器人 USD 模型文件，用于 ROS2 Control 仿真。

## 克隆与初始化

```bash
# 克隆仓库
git clone git@github.com:fiveages-sim/robot_usds.git
cd robot_usds

# 安装 Git LFS（若未安装）
git lfs install

# 拉取 LFS 文件
git lfs pull
```

## 模型

- Gripper（夹爪）
    - ChangingTek_AG2F120S
    - ChangingTek_AG2F90_C
        - ChangingTek_AG2F90_C 的软垫版本（刚体模拟）
- Manipulator（机械臂）
    - DobotCR5
        - Dobot CR5 双臂
    - Elite_EC66
    - Agilex Piper

## 文件结构

项目核心目录为 `robots`，包含以下子目录与资源：

```bash
robots/
  grippers/           # 夹爪模型及按功能拆分的配置
  manipulators/       # 机械臂模型、环境示例与配置
  README.md
  LICENSE
```

`manipulators/*/envs/` 下的部分场景依赖外部环境资源（纹理、资产、共享组件等）。

## 使用环境内容

如需使用环境的内容，请在与 `robots` 同级的位置新建一个 `environment` 文件夹，并在该文件夹内克隆 `fiveages_env`：

```bash
# 进入 robots 的上级目录（示例路径按需调整）
cd /home/fiveages/Documents/usd

mkdir -p environment
cd environment

# 克隆环境资源仓库
git clone https://github.com/fiveages-sim/fiveages-env-usds fiveages_env
```

完成后目录结构应类似：

```bash
/home/fiveages/Documents/usd/
  robots/
  environment/
    fiveages_env/
```

这样，依赖环境资源的场景即可正常引用 `environment/fiveages_env` 中的内容。
