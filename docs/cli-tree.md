# CLI 树

以下只列出当前已实现的命令。规划能力不放进 CLI 树，避免把文档蓝图误当成可执行接口。

## 顶层命令

```text
termcap
├── record [OUTPUT_PATH]       # 录制 PTY 会话为 asciicast v2
├── replay INPUT_FILE          # 在当前终端重放 CAST
├── render INPUT [OUTPUT]      # CAST→SVG/GIF，或 SVG→GIF
├── svg2gif INPUT [OUTPUT]     # 独立 SVG→GIF 入口
├── config ...                 # 查看和修改持久配置
├── template ...               # 管理自定义 SVG 模板
├── --version
└── --help
```

直接运行 `termcap` 会输出主帮助信息。

## 录制与重放

```text
termcap record [OUTPUT_PATH]
├── -c, --command TEXT         # 默认 $SHELL
└── -g, --geometry WIDTHxHEIGHT

termcap replay INPUT_FILE
├── -s, --speed FLOAT
└── -i, --idle-time-limit FLOAT
```

- `record` 默认读取当前终端尺寸；短演示建议显式设置 geometry。
- `record -c` 会在 stdin EOF 后继续 drain PTY，避免短命令生成只有 header 的空 CAST。
- `replay --idle-time-limit` 可以压缩长时间无输出的等待。

## 渲染与 GIF

```text
termcap render INPUT [OUTPUT]
├── --format [svg|gif]
├── -D, --loop-delay INTEGER
├── -m, --min-duration INTEGER
├── -M, --max-duration INTEGER
├── -s, --still-frames
├── -t, --template TEXT
├── --speed FLOAT
├── --fps INTEGER
└── --loop INTEGER

termcap svg2gif INPUT.svg [OUTPUT.gif]
├── --speed FLOAT
├── --fps INTEGER
└── --loop INTEGER
```

输入/输出矩阵：

| 输入 | 输出 | 命令 |
|---|---|---|
| `.cast` | `.svg` | `termcap render demo.cast demo.svg` |
| `.cast` | `.gif` | `termcap render demo.cast demo.gif --format gif` |
| `.svg` | `.gif` | `termcap render demo.svg demo.gif --format gif` |
| `.svg` | `.gif` | `termcap svg2gif demo.svg demo.gif` |

`--format cast` 未实现，因此不会出现在帮助里。

## 配置

```text
termcap config
├── show
├── get SECTION KEY
├── set SECTION KEY VALUE
├── reset
└── templates
```

## 模板

```text
termcap template
├── list
├── install NAME TEMPLATE_FILE
└── remove NAME
```

内置模板随 wheel 一起安装；自定义模板写入用户配置目录，不修改包源码。
