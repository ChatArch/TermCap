from pathlib import Path

import click

from termcap.player import ReplayError, play


def register_replay_command(main):
    @main.command()
    @click.argument(
        "input_file",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
    )
    @click.option(
        "-s",
        "--speed",
        type=click.FloatRange(min=0, min_open=True),
        default=1.0,
        show_default=True,
        help="Playback speed",
    )
    @click.option(
        "-i",
        "--idle-time-limit",
        type=click.FloatRange(min=0),
        help="Limit idle time to N seconds",
    )
    def replay(input_file, speed, idle_time_limit):
        """Replay an asciicast in the current terminal."""
        try:
            play(str(input_file), speed, idle_time_limit)
        except ReplayError as exc:
            raise click.ClickException(str(exc)) from exc
