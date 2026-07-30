# CLI Tree

Only implemented commands are listed here. Planned capabilities stay out of the CLI tree so documentation blueprints cannot be mistaken for executable interfaces.

## Top-level commands

```text
termcap
├── record [OUTPUT_PATH]       # Capture a PTY session as asciicast v2
├── replay INPUT_FILE          # Replay a CAST in the current terminal
├── render INPUT [OUTPUT]      # CAST→SVG/GIF or SVG→GIF
├── svg2gif INPUT [OUTPUT]     # Dedicated SVG→GIF entry point
├── config ...                 # Inspect and update persistent settings
├── template ...               # Manage custom SVG templates
├── --version
└── --help
```

Running `termcap` without a subcommand prints the main help page.

## Capture and replay

```text
termcap record [OUTPUT_PATH]
├── -c, --command TEXT         # Defaults to $SHELL
└── -g, --geometry WIDTHxHEIGHT

termcap replay INPUT_FILE
├── -s, --speed FLOAT
└── -i, --idle-time-limit FLOAT
```

- `record` uses the current terminal size by default; set geometry explicitly for compact demos.
- `record -c` continues draining the PTY after stdin EOF, so short commands do not produce header-only CAST files.
- `replay --idle-time-limit` compresses long periods without output.

## Rendering and GIF

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

Input/output matrix:

| Input | Output | Command |
|---|---|---|
| `.cast` | `.svg` | `termcap render demo.cast demo.svg` |
| `.cast` | `.gif` | `termcap render demo.cast demo.gif --format gif` |
| `.svg` | `.gif` | `termcap render demo.svg demo.gif --format gif` |
| `.svg` | `.gif` | `termcap svg2gif demo.svg demo.gif` |

`--format cast` is not implemented and is intentionally absent from help.

## Configuration

```text
termcap config
├── show
├── get SECTION KEY
├── set SECTION KEY VALUE
├── reset
└── templates
```

## Templates

```text
termcap template
├── list
├── install NAME TEMPLATE_FILE
└── remove NAME
```

Built-in templates ship inside the wheel. Custom templates are written to the user configuration directory rather than the package source tree.
