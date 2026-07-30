# TermCap

[![测试](https://github.com/ChatArch/TermCap/actions/workflows/ci.yml/badge.svg)](https://github.com/ChatArch/TermCap/actions/workflows/ci.yml)
[![文档](https://github.com/ChatArch/TermCap/actions/workflows/deploy.yml/badge.svg)](https://arch.gh.wzhecnu.cn/TermCap/)
[![PyPI](https://img.shields.io/pypi/v/termcap.svg)](https://pypi.org/project/termcap/)

TermCap 是一个 Python 终端录制与渲染工具：把 PTY 会话保存为 asciicast v2，并输出 SVG 动画、静态 SVG 帧或 GIF。

- [完整文档](https://arch.gh.wzhecnu.cn/TermCap/)
- [快速开始](https://arch.gh.wzhecnu.cn/TermCap/quickstart/)
- [CLI 树](https://arch.gh.wzhecnu.cn/TermCap/cli-tree/)
- [录制与渲染](https://arch.gh.wzhecnu.cn/TermCap/rendering/)
- [英文版](README.en.md)

## 核心能力

- 交互 shell 与单命令 PTY 录制
- 兼容 asciinema 的 `.cast` 格式
- ANSI 颜色、光标、文本样式和宽字符渲染
- 模板化 SVG 动画与 16 套内置主题
- CAST→SVG、CAST→GIF、SVG→GIF
- 关键帧确定性采样和 Chrome viewport 自动校正

<p align="center">
  <img src="docs/examples/awesome_window_frame_js.svg" width="80%" alt="TermCap 终端动画示例">
</p>

## 安装

TermCap 支持 Linux、macOS 和 BSD，需要 Python 3.8 或更高版本。GIF 导出需要 Google Chrome。

```bash
python -m pip install termcap
termcap --version
```

## 最短工作流

```bash
termcap record demo.cast -g 80x20
termcap render demo.cast demo.svg
termcap render demo.cast demo.gif --format gif
```

录制单条命令：

```bash
termcap record tests.cast -g 100x24 -c "python -m pytest -q"
```

已有 SVG 转 GIF：

```bash
termcap svg2gif demo.svg demo.gif --speed 1 --loop 0
```

## 文档开发

```bash
python -m pip install -e '.[dev,docs]'
mkdocs serve
mkdocs build --strict
```

## 许可证

MIT License
