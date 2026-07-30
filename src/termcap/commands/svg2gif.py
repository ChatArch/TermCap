from pathlib import Path

import click
from rich.console import Console

from termcap.gif_converter import convert_svg_to_gif


def register_svg2gif_command(main):
    @main.command("svg2gif")
    @click.argument(
        "input_file",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
    )
    @click.argument(
        "output_path",
        required=False,
        type=click.Path(dir_okay=False, path_type=Path),
    )
    @click.option(
        "--speed",
        type=click.FloatRange(min=0, min_open=True),
        default=1.0,
        show_default=True,
        help="Playback speed factor",
    )
    @click.option(
        "--fps",
        type=click.IntRange(min=1),
        default=20,
        show_default=True,
        help="Fallback sampling FPS for SVGs without discrete keyframes",
    )
    @click.option(
        "--loop",
        type=click.IntRange(min=0),
        default=0,
        show_default=True,
        help="GIF loop count (0 = infinite)",
    )
    def svg2gif(input_file, output_path, speed, fps, loop):
        """Convert an animated SVG file to GIF."""
        output_path = output_path or input_file.with_suffix(".gif")
        console = Console()
        try:
            frames, duration_ms = convert_svg_to_gif(
                input_file,
                output_path,
                speed=speed,
                fps=fps,
                loop=loop,
                progress=lambda message: console.print(f"[cyan]•[/cyan] {message}"),
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

        console.print("[bold green]✓ SVG 转 GIF 完成[/bold green]")
        click.echo(f"GIF output: {output_path}")
        click.echo(f"Frames: {frames}, duration: {duration_ms:.0f}ms")
