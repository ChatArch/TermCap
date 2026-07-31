# Changelog

本文档记录 TermCap 的用户可见变更。

## 未发布

### 文档

- 新增可复现的终端录制脚本及配套 SVG/GIF 资产。
- 在 README、文档首页、快速开始和示例页嵌入当前工具链生成的视觉示例与完整命令。

## 0.2.1 — 2026-07-29

### 新增

- 新增 `termcap svg2gif`，支持将动画 SVG 导出为 GIF。
- 扩展 `termcap render`，支持 CAST→GIF 和 SVG→GIF。
- 新增 `--speed`、`--fps`、`--loop` GIF 控制参数。
- 新增 Chrome 支持的离散关键帧浏览器验收测试。
- 新增 ChatArch MkDocs 中英文文档入口、CLI 树、快速开始、渲染说明和能力边界。

### 修复

- 修复 Selenium outer window 与 viewport 高度不同导致 GIF 底部被裁切的问题。
- 修复 CSS delay 与 WAAPI current time 重复推进导致关键帧丢失的问题。
- 修复百分比关键帧边界向下取整导致下一帧未生效的问题。
- 修复 `record -c` 在 stdin EOF 时饿死 PTY 读取、生成空 CAST 的问题。
- 修复子进程退出后未 drain PTY 最终输出的问题。
- 修复 PyPI wheel 不包含内置 SVG 模板的问题。

### 变更

- TermCap SVG 使用离散关键帧采样；普通 SVG 才回退到固定 FPS。
- 截图前等待字体加载和双 `requestAnimationFrame`，并严格校验截图像素尺寸。
- 发布工作流切换到 PyPI Trusted Publisher/OIDC，不再使用长期 `PYPI_API_TOKEN`。
- 文档站切换到 ChatArch Pages 路径 `https://arch.gh.wzhecnu.cn/TermCap/`。
