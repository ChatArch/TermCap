# Capture and Rendering

TermCap separates terminal media processing into PTY capture, terminal-state reconstruction, and media export. Each layer has a stable data contract that can be validated and reused independently.

<div class="grid cards" markdown>

-   **Capture**

    PTY output → asciicast v2 `.cast`

-   **Render**

    CAST events → `pyte.Screen` → SVG frames

-   **Export**

    SVG timeline → deterministic Chrome sampling → GIF

</div>

## PTY → CAST

`termcap record` starts a child process with `pty.fork()`, applies terminal geometry, and writes output events as asciicast v2:

```json
{"version": 2, "width": 80, "height": 20}
[0.15, "o", "hello\r\n"]
```

The recorder:

- uses an incremental UTF-8 decoder so multibyte characters survive chunk boundaries;
- preserves ANSI control sequences, colors, and cursor movement;
- stops polling stdin after EOF while continuing to read the PTY;
- drains the PTY through EOF/EIO after the child exits so final output is not lost.

## CAST → SVG { #cast-to-svg }

```bash
termcap render demo.cast demo.svg
```

Events are fed into `pyte.Stream`, and terminal screen buffers are stored at meaningful timestamps. Generated SVGs expose a stable DOM contract:

```text
#terminal      outer SVG and final capture target
#screen        terminal viewport
#screen_view   vertically stacked discrete frames
```

Animation uses `@keyframes roll` with `steps(1,end)`, preventing interpolated half-frames between terminal states.

### Timing controls

- `--min-duration` merges excessively dense output updates;
- `--max-duration` caps long idle gaps;
- `--loop-delay` controls how long the final frame remains before looping.

## CAST → GIF { #cast-to-gif }

```bash
termcap render demo.cast demo.gif --format gif
```

TermCap renders an intermediate SVG in a temporary directory and sends it through the same SVG→GIF backend. The intermediate file is not written into the repository.

## SVG → GIF { #svg-to-gif }

```bash
termcap svg2gif demo.svg demo.gif
```

For TermCap/termtosvg-style SVGs, the converter:

1. reads `--animation-duration`;
2. extracts discrete `translateY(...)` keyframe percentages;
3. freezes animation just after each keyframe boundary;
4. waits for `document.fonts.ready` and two animation frames;
5. grows the Chrome outer window until `innerWidth/innerHeight` contain `#terminal`;
6. verifies captured pixel dimensions against the expected SVG size;
7. quantizes frame delays to GIF's 10ms precision while compensating cumulative error.

Generic SVGs without recognizable discrete keyframes fall back to uniform `--fps` sampling.

## Avoid clipping and blank space

### Bottom or right edge is clipped

Selenium `set_window_size()` controls the outer window, not the page viewport. TermCap reads `window.innerWidth/innerHeight` and grows the outer window dynamically. If the viewport still cannot contain the SVG, conversion fails instead of silently writing an incomplete GIF.

### Large blank area inside the terminal

This belongs to the recorded terminal geometry rather than browser padding. Use a compact geometry for short demos:

```bash
termcap record short.cast -g 80x12 -c "python demo.py"
```

TermCap does not trim rows based on the final frame because earlier frames or full-screen programs such as `vim` and `htop` may use the complete terminal viewport.

### Black frames or shifted fonts

The converter waits for fonts and two RAF ticks rather than relying only on fixed sleeps. A screenshot smaller than the target size is rejected immediately.

## Acceptance checklist

Cover at least:

- short commands and interactive shells;
- ANSI colors and cursor movement;
- CJK/wide characters;
- carriage-return line updates;
- CAST→SVG, CAST→GIF, and SVG→GIF;
- GIF dimensions equal to the SVG viewBox and total frame duration close to the SVG timeline.
