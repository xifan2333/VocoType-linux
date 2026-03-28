# Changelog

All notable changes to VoCoType Linux IBus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-03-28 (pre-release)

### Added

- **新增 LLM 后处理链路（长句模式）**：
  - `Shift+F9` 新增长句模式后处理（ASR + 标点 + 可选 SLM/LLM 润色）
  - 新增本地一次性加载 worker：按下预热、释放后自动回收
  - 新增后处理基准脚本：`scripts/benchmark_slm_pipeline.py`
  - 新增后处理单元测试：`test/test_slm_polisher.py`

### Changed

- **安装脚本增强（IBus/Fcitx5）**：
  - SLM 保持可选安装，不启用时不安装模型
  - 启用后可交互选择：
    - 本地模型（`local_ephemeral`）
    - 远程 API（`remote`）
  - 远程 API 模式支持交互写入：`model`、`endpoint`、`api_key`
- **默认阈值优化**：
  - `min_chars` 默认从 `20` 下调到 `8`，减少长句模式被 `too_short` 跳过的概率
- **远程稳定性改进**：
  - 远程请求失败时增加“直连重试（绕过代理）”机制，降低代理环境下的偶发失败

### Documentation

- 更新根文档、IBus、Fcitx5 文档：
  - 新增本地模型与远程 API 两种配置方式
  - 补充 SLM 参数说明和使用建议
  - 补充失败提示与调试方式

## [2.1.2] - 2026-01-21

### Fixed

- **修复**：Ctrl+Space 无法切换 Rime ascii_mode 的问题
  - **问题**：用户在 `default.custom.yaml` 中配置 `Ctrl+Space` 切换 `ascii_mode`，但在 VoCoType 中不生效
  - **原因**：IBus 和 Fcitx5 后端错误地将 `Ctrl+Space` 作为输入法切换热键拦截，导致按键未传递给 Rime
  - **解决**：移除 `Ctrl+Space` 拦截，仅保留 `Super+Space` 作为输入法切换热键，允许 Rime 按照用户配置处理 `Ctrl+Space`
  - **影响范围**：IBus (`ibus/engine.py:574-579`) 和 Fcitx5 (`fcitx5/addon/vocotype.cpp:441-447`) 后端

## [2.1.1] - 2026-01-20

### Changed

- **Python 版本要求调整**：
  - 支持版本：Python 3.11–3.12
  - **不再支持 Python 3.10**

- **PyGObject 版本限制**：
  - 限制为 `<3.51`，避免 Ubuntu 22.04 因缺少 `libgirepository-2` 导致安装失败

- **安装脚本改进**：
  - 项目/用户级虚拟环境优先使用 `uv` 工具
  - 系统 Python 安装仅在用户明确选择时才遍历

### Fixed

- **修复**：Fcitx5 插件路径检测
  - 补充 `/usr/lib/x86_64-linux-gnu/fcitx5` 路径（Ubuntu 系统修复）
  - 确保在 Debian/Ubuntu 系统上正确检测插件目录

### Documentation

- **更新**：Debian/Ubuntu 依赖说明
  - 说明 Ubuntu 22.04 的 librime/ibus-rime 版本偏旧
  - 建议使用 Rime 功能时手动编译安装 librime + ibus-rime

### Compatibility Notes

- ⚠️ **不兼容变更**：不再支持 Python 3.10，请使用 Python 3.11 或 3.12
- ⚠️ **Ubuntu 22.04**：若使用 Rime 功能，建议手动编译安装 librime + ibus-rime

## [2.1.0]

### Changed

- **代码重构**：重整代码结构，提升可维护性
- **功能增强**：增加输入方案选择功能

### Fixed

- **修复**：多个安装不稳定问题
  - 提升安装成功率
  - 改进依赖检测和安装流程

## [2.0.0]

### Added

- **Fcitx5 支持**：新增 Fcitx5 输入法框架支持
  - 项目从 `vocotype-ibus` 更名为 `vocotype-linux`
  - 同时支持 IBus 和 Fcitx5 两种输入法框架
  - 用户可根据系统环境选择对应的安装脚本

### Changed

- **项目更名**：`vocotype-ibus` → `vocotype-linux`
  - 反映多框架支持的定位
  - 更广泛的 Linux 桌面环境兼容性

## [1.1.0] - 2026-01-02

### Added

#### 🎯 Rime 拼音输入集成（可选）

- **完整版输入法**：现在可以选择安装"完整版"，在同一个输入法内同时支持：
  - **F9 语音输入**：按住 F9 说话，松开后自动识别
  - **拼音输入**：直接打字，Rime 引擎处理拼音输入并显示候选词
  - 一个输入法搞定所有需求，无需切换

- **纯语音版（推荐新手）**：保持原有的纯语音输入功能
  - 仅 F9 语音输入
  - 依赖少，安装简单
  - 可与其他拼音输入法（如 ibus-rime）配合使用

- **Rime 配置共享**：完整版使用 `~/.config/ibus/rime/` 作为配置目录
  - 与 ibus-rime 共享词库和配置
  - 如果已经配置过 ibus-rime，所有设置和词库都会自动继承
  - 无需重复配置

- **优雅降级**：即使安装了完整版，如果 pyrime 不可用，引擎会自动切换到纯语音模式

#### 🚀 安装体验改进

- **交互式安装向导**：
  ```
  请选择安装版本：
    [1] 纯语音版（推荐新手）- 仅语音输入，依赖少
    [2] 完整版 - 语音 + Rime 拼音输入，一个输入法全搞定
  ```

- **多平台自动检测与安装**：
  - 自动检测 Linux 发行版（Fedora/RHEL、Debian/Ubuntu、Arch Linux）
  - 提供对应的系统依赖安装命令
  - 可选择自动安装或手动安装系统依赖
  - 智能检测 librime-devel 是否已安装，避免重复安装

- **Python 环境选择**：安装时可选择：
  - 项目虚拟环境（推荐）
  - 用户级虚拟环境
  - 系统 Python

- **依赖管理优化**：
  - 优先使用 `uv` 工具（如果可用）创建虚拟环境和安装依赖
  - 自动回退到 `python3 -m venv` 和 `pip`

### Changed

#### ⚙️ 技术架构改进

- **Rime 集成方式完全重写**：
  - **移除**：基于 IBus InputContext 代理方式（存在架构缺陷）
  - **新增**：直接使用 `pyrime` 库调用 `librime`
  - **优势**：
    - 无阻塞、无超时问题
    - 更高效的按键处理
    - 更可靠的候选词显示

- **按键处理优化**：
  - 正确的 IBus 到 Rime modifier mask 转换
  - 支持 Shift、Ctrl、Alt、Lock 等修饰键
  - 不再手动调用 `post_process_key_event()`（由 IBus 框架自动处理）

- **UI 更新改进**：
  - 使用 Rime Context API 直接获取预编辑文本和候选词
  - 正确设置下划线样式和光标位置
  - 支持候选词注释（comment）显示

#### 📦 依赖变更

- **核心依赖**（必需）：
  ```toml
  sounddevice==0.5.2
  librosa==0.11.0
  soundfile==0.13.1
  funasr_onnx==0.4.1
  jieba==0.42.1
  PyGObject>=3.42.0
  modelscope==1.30.0
  torch>=2.9.1
  ```

- **可选依赖**（新增）：
  ```toml
  [project.optional-dependencies]
  rime = ["pyrime>=0.2.1"]
  full = ["pyrime>=0.2.1"]
  ```

- **系统依赖**（完整版需要）：
  - Fedora/RHEL: `librime-devel ibus-rime`
  - Debian/Ubuntu: `librime-dev ibus-rime`
  - Arch Linux: `librime ibus-rime`

### Fixed

- **修复**：引擎激活超时问题
  - **问题**：使用 InputContext 代理 Rime 时，`set_engine()` 调用阻塞导致超时
  - **解决**：切换到 pyrime 直接集成，彻底消除阻塞

- **修复**：GObject 警告
  - **问题**：`g_object_is_floating: assertion 'G_IS_OBJECT (object)' failed`
  - **原因**：错误地手动调用 `post_process_key_event()`
  - **解决**：移除手动调用，由 IBus 框架自动处理

- **修复**：pyrime 二进制兼容性问题
  - **问题**：Python 3.12 构建的 .so 文件无法在 Python 3.13 中使用
  - **解决**：为每个 Python 版本正确编译对应的二进制模块

### Documentation

- **完全重写 README**：
  - 新增两种版本对比表
  - 详细的分版本安装指南
  - 功能对比和使用场景说明
  - 常见问题解答更新

- **安装脚本改进**：
  - 清晰的版本选择提示
  - 多平台支持说明
  - 依赖安装引导

## [1.0.0] - Initial Release

### Added

- 基于 VoCoType 核心引擎的 IBus 输入法实现
- F9 PTT (Push-to-Talk) 语音输入
- 基于 FunASR Paraformer 的离线语音识别
- 交互式音频设备配置向导
- 自动模型下载
- 用户级安装支持（`~/.local/`）

### Features

- 100% 离线，隐私安全
- 0.1 秒级识别响应
- 700MB 内存占用
- 纯 CPU 推理，无需 GPU
- 中英混合输入支持
- 识别准确率 >95%

---

## 升级指南

### 从 1.0.0 升级到 1.1.0

#### 选项 1：保持纯语音版

如果您只需要语音输入功能，无需任何操作。现有安装继续正常工作。

#### 选项 2：升级到完整版（语音 + Rime）

1. **安装系统依赖**：

   ```bash
   # Fedora / RHEL
   sudo dnf install librime-devel ibus-rime

   # Ubuntu / Debian
   sudo apt install librime-dev ibus-rime

   # Arch Linux
   sudo pacman -S librime ibus-rime
   ```

2. **安装 pyrime**：

   ```bash
   # 如果使用项目虚拟环境
   .venv/bin/pip install pyrime

   # 如果使用用户级虚拟环境
   ~/.local/share/vocotype/.venv/bin/pip install pyrime
   ```

3. **重启 IBus**：

   ```bash
   ibus restart
   ```

4. **验证**：切换到 VoCoType 输入法，尝试：
   - 按住 F9 说话（语音输入）
   - 直接打字（拼音输入）

#### 全新安装

建议重新运行安装脚本，它会引导您选择合适的版本：

```bash
cd vocotype-cli
./scripts/install-ibus.sh
```

---

## 技术细节

### Rime 集成实现

**v1.0.0（已移除）**：
```python
# ❌ 旧方法：通过 InputContext 代理
self._rime_context = IBus.InputContext(...)
self._rime_context.set_engine("rime")  # 阻塞！
```

**v1.1.0（当前）**：
```python
# ✅ 新方法：直接使用 pyrime
from pyrime.session import Session
self._rime_session = Session(traits=traits, api=api)
handled = self._rime_session.process_key(keyval, rime_mask)
```

### 配置目录结构

```
~/.config/
├── vocotype/
│   └── audio.conf          # VoCoType 音频配置
└── ibus/
    └── rime/               # Rime 配置（与 ibus-rime 共享）
        ├── default.yaml
        ├── luna_pinyin.yaml
        └── ...

~/.local/share/
├── vocotype/               # VoCoType 安装目录
│   ├── app/
│   ├── ibus/
│   └── .venv/
└── ibus/
    └── component/
        └── vocotype.xml    # IBus 组件配置
```

---

## 致谢

- **[pyrime](https://github.com/TypeDuck-HK/pyrime)** - 优秀的 librime Python 绑定
- **[ibus-rime](https://github.com/rime/ibus-rime)** - Rime IBus 输入法，为我们的集成提供了配置共享基础
- **[RIME](https://rime.im/)** - 强大的开源中文输入法引擎
