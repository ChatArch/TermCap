# Quick Start

<div class="grid cards" markdown>

-   **Interactive capture**

    Enter a child shell, run multiple commands, and finish with `exit` or ++ctrl+d++.

-   **Single-command capture**

    Use `-c` for scripts, tests, or one-shot commands. Capture ends when the command exits.

-   **Media export**

    Render one `.cast` file as SVG, GIF, or a directory of still SVG frames.

</div>

## Install

TermCap supports Linux, macOS, and BSD and requires Python 3.8 or newer. GIF export also needs a working Google Chrome installation; TermCap prepares and caches ChromeDriver on first use.

```bash
python -m pip install termcap
termcap --version
```

## See the complete result first

Both images come from the same terminal recording. TermCap first produces a scalable animated SVG, then exports the GIF deterministically from the same timeline.

### SVG animation

<p align="center">
  <a href="../../assets/examples/quickstart.svg">
    <img src="../../assets/examples/quickstart.svg" width="100%" alt="TermCap SVG quick-start example">
  </a>
</p>

### GIF export

<p align="center">
  <a href="../../assets/examples/quickstart.gif">
    <img src="../../assets/examples/quickstart.gif" width="100%" alt="TermCap GIF quick-start example">
  </a>
</p>

[See the generator script and complete commands](examples/index.md#reproducible-svg-gif)

## Capture a terminal

### Interactive shell

```bash
termcap record demo.cast -g 80x20
```

Run commands normally inside the child shell, then finish with:

```bash
exit
```

### One command

```bash
termcap record tests.cast -g 100x24 -c "python -m pytest -q"
```

Command mode keeps reading the PTY until the child exits and drains buffered output, including short-lived commands.

## Replay a CAST

```bash
termcap replay demo.cast
termcap replay demo.cast --speed 2
termcap replay demo.cast --idle-time-limit 2
```

## Render SVG

```bash
termcap render demo.cast demo.svg
```

Choose a template:

```bash
termcap render demo.cast demo.svg -t window_frame
```

Write independent still frames:

```bash
termcap render demo.cast demo_frames --still-frames
```

## Export GIF

Convert CAST directly to GIF:

```bash
termcap render demo.cast demo.gif --format gif
```

Convert an existing SVG:

```bash
termcap svg2gif demo.svg demo.gif
```

Change playback speed and looping:

```bash
termcap svg2gif demo.svg demo-fast.gif --speed 2 --loop 0
```

When a TermCap SVG exposes discrete terminal keyframes, `--fps` does not create duplicate frames. It is used only as a fallback for generic SVG animations without recognizable keyframes.

## Next

- [Inspect the complete CLI tree](cli-tree.md)
- [Understand capture and rendering](rendering.md)
- [Choose or build a template](templates.md)
