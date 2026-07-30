# Capability Map

## Implemented and verified

| Capability | Status | Contract |
|---|---|---|
| PTY capture | Implemented | Writes asciicast v2 from interactive shells and `-c` commands |
| CAST replay | Implemented | Supports playback speed and idle-time caps |
| Terminal-state reconstruction | Implemented | Uses `pyte` and preserves ANSI styles, cursor state, and wide characters |
| SVG animation | Implemented | Stable DOM IDs, discrete CSS keyframes, and template-based UI |
| Still SVG frames | Implemented | Writes one independent SVG per terminal state |
| CAST → GIF | Implemented | Reuses the SVG intermediate representation and timeline |
| SVG → GIF | Implemented | Keyframe-first sampling with FPS fallback for generic SVGs |
| Viewport correction | Implemented | Grows the viewport or fails explicitly when capture would be incomplete |
| Built-in templates | Implemented | Ships 16 templates in wheel package data |
| MkDocs documentation | Implemented | Suffix-based Chinese/English i18n, CLI tree, and task-oriented navigation |

## Safety and defaults

- Terminal rows are not trimmed automatically; geometry is part of the capture contract.
- Unimplemented capabilities are not advertised as placeholder CLI options.
- GIF output loops forever by default with `--loop 0`.
- `--speed 1.0` preserves recorded time; speed changes affect output frame delays.
- Browser drivers are cached in the user cache directory rather than the repository.
- Built-in templates load from package data; source `docs/examples` files remain development references.

## Out of current scope

- MP4/WebM export
- audio capture and synchronization
- Windows ConPTY capture
- CAST editing or CAST→CAST resampling
- automatic row trimming based on the final frame
- full implementation of the historical WAAPI renderer mode mentioned by template docs

## Verification layers

<div class="grid cards" markdown>

-   **Unit tests**

    Parser, config, templates, timing quantization, keyframe plans, viewport behavior, and CLI contracts.

-   **Browser test**

    Red/green/blue discrete keyframes enter the GIF in order and captured dimensions equal the SVG.

-   **Real capture acceptance**

    ANSI color, CJK wide characters, progressive output, and carriage-return updates pass through CAST→SVG→GIF.

-   **Release acceptance**

    Wheel/sdist checks, template package data, MkDocs strict build, Trusted Publisher, and clean PyPI install.

</div>
