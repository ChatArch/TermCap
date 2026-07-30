# TermCap

[![Tests](https://github.com/ChatArch/TermCap/actions/workflows/ci.yml/badge.svg)](https://github.com/ChatArch/TermCap/actions/workflows/ci.yml)
[![Docs](https://github.com/ChatArch/TermCap/actions/workflows/deploy.yml/badge.svg)](https://arch.gh.wzhecnu.cn/TermCap/)
[![PyPI](https://img.shields.io/pypi/v/termcap.svg)](https://pypi.org/project/termcap/)

TermCap is a Python terminal capture and rendering tool. It records PTY sessions as asciicast v2 and exports SVG animations, still SVG frames, or GIF files.

- [Documentation](https://arch.gh.wzhecnu.cn/TermCap/en/)
- [Quick start](https://arch.gh.wzhecnu.cn/TermCap/en/quickstart/)
- [CLI tree](https://arch.gh.wzhecnu.cn/TermCap/en/cli-tree/)
- [Capture and rendering](https://arch.gh.wzhecnu.cn/TermCap/en/rendering/)
- [中文版](README.md)

## Core capabilities

- interactive shell and single-command PTY capture
- asciinema-compatible `.cast` files
- ANSI color, cursor, text-style, and wide-character rendering
- template-based SVG animation with 16 built-in themes
- CAST→SVG, CAST→GIF, and SVG→GIF
- deterministic keyframe sampling and automatic Chrome viewport correction

<p align="center">
  <img src="docs/examples/awesome_window_frame_js.svg" width="80%" alt="TermCap terminal animation example">
</p>

## Install

TermCap supports Linux, macOS, and BSD and requires Python 3.8 or newer. GIF export requires Google Chrome.

```bash
python -m pip install termcap
termcap --version
```

## Shortest workflow

```bash
termcap record demo.cast -g 80x20
termcap render demo.cast demo.svg
termcap render demo.cast demo.gif --format gif
```

Capture one command:

```bash
termcap record tests.cast -g 100x24 -c "python -m pytest -q"
```

Convert an existing SVG:

```bash
termcap svg2gif demo.svg demo.gif --speed 1 --loop 0
```

## Documentation development

```bash
python -m pip install -e '.[dev,docs]'
mkdocs serve
mkdocs build --strict
```

## License

MIT License
