from pathlib import Path

import click
from rich.console import Console

from termcap.commands.common import get_default_settings
from termcap.gif_converter import convert_cast_to_gif, convert_svg_to_gif
from termcap.parser.asciicast import read_records
from termcap.renderer import render_animation, render_still_frames


def register_render_command(main):
    @main.command()
    @click.argument(
        "input_path",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
    )
    @click.argument("output_path", required=False, type=click.Path(path_type=Path))
    @click.option(
        "--format",
        "output_format",
        type=click.Choice(["svg", "gif"]),
        help="Output format; inferred from output extension when omitted",
    )
    @click.option("-D", "--loop-delay", type=int, help="Delay between animation loops (ms)")
    @click.option("-m", "--min-duration", type=int, help="Minimum frame duration (ms)")
    @click.option("-M", "--max-duration", type=int, help="Maximum frame duration (ms)")
    @click.option("-s", "--still-frames", is_flag=True, help="Output still SVG frames")
    @click.option("-t", "--template", help="SVG template to use")
    @click.option(
        "--speed",
        type=click.FloatRange(min=0, min_open=True),
        default=1.0,
        show_default=True,
        help="GIF playback speed factor",
    )
    @click.option(
        "--fps",
        type=click.IntRange(min=1),
        default=20,
        show_default=True,
        help="Fallback GIF sampling FPS",
    )
    @click.option(
        "--loop",
        type=click.IntRange(min=0),
        default=0,
        show_default=True,
        help="GIF loop count (0 = infinite)",
    )
    def render(
        input_path,
        output_path,
        output_format,
        loop_delay,
        min_duration,
        max_duration,
        still_frames,
        template,
        speed,
        fps,
        loop,
    ):
        """Render an asciicast to SVG/GIF, or an animated SVG to GIF."""
        defaults = get_default_settings()
        template = template or defaults["template"]
        min_duration = min_duration if min_duration is not None else defaults["min_duration"]
        max_duration = max_duration if max_duration is not None else defaults["max_duration"]
        loop_delay = loop_delay if loop_delay is not None else defaults["loop_delay"]

        input_suffix = input_path.suffix.lower()
        if output_format is None:
            if still_frames:
                output_format = "svg"
            elif output_path and output_path.suffix.lower() == ".gif":
                output_format = "gif"
            else:
                output_format = "svg"

        if still_frames and output_format != "svg":
            raise click.UsageError("--still-frames only supports SVG output")
        if input_suffix == ".svg" and output_format != "gif":
            raise click.UsageError("SVG input only supports GIF output")
        if input_suffix not in {".cast", ".svg"}:
            raise click.UsageError("Input must be an .cast file, or an .svg file for GIF output")

        if output_path is None:
            if still_frames:
                output_path = input_path.parent / f"{input_path.stem}_frames"
            else:
                output_path = input_path.with_suffix(f".{output_format}")

        console = Console()
        progress = lambda message: console.print(f"[cyan]•[/cyan] {message}")
        try:
            if output_format == "gif" and input_suffix == ".svg":
                frames, duration_ms = convert_svg_to_gif(
                    input_path,
                    output_path,
                    speed=speed,
                    fps=fps,
                    loop=loop,
                    progress=progress,
                )
                console.print("[bold green]✓ SVG 转 GIF 完成[/bold green]")
                click.echo(f"GIF output: {output_path}")
                click.echo(f"Frames: {frames}, duration: {duration_ms:.0f}ms")
                return

            if output_format == "gif":
                frames, duration_ms = convert_cast_to_gif(
                    input_path,
                    output_path,
                    template_name=template,
                    min_duration=min_duration,
                    max_duration=max_duration,
                    loop_delay=loop_delay,
                    speed=speed,
                    fps=fps,
                    loop=loop,
                    progress=progress,
                )
                console.print("[bold green]✓ CAST 转 GIF 完成[/bold green]")
                click.echo(f"GIF output: {output_path}")
                click.echo(f"Frames: {frames}, duration: {duration_ms:.0f}ms")
                return

            records_iter = read_records(str(input_path))
            try:
                header = next(records_iter)
            except StopIteration as exc:
                raise click.ClickException("Empty input file") from exc

            if still_frames:
                with console.status("正在渲染 SVG 静帧...", spinner="dots"):
                    render_still_frames(
                        records_iter,
                        header,
                        str(output_path),
                        template,
                        min_duration,
                        max_duration,
                        loop_delay,
                    )
                console.print("[bold green]✓ SVG 静帧渲染完成[/bold green]")
                click.echo(f"SVG frames: {output_path}")
            else:
                with console.status("正在渲染 SVG 动画...", spinner="dots"):
                    render_animation(
                        records_iter,
                        header,
                        str(output_path),
                        template,
                        min_duration,
                        max_duration,
                        loop_delay,
                    )
                console.print("[bold green]✓ SVG 动画渲染完成[/bold green]")
                click.echo(f"SVG animation: {output_path}")
        except click.ClickException:
            raise
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
