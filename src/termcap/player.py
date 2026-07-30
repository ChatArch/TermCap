import sys
import time
from typing import Optional

from termcap.parser.asciicast import AsciiCastV2Event, AsciiCastV2Header, read_records


class ReplayError(RuntimeError):
    """Raised when a cast cannot be replayed."""


def play(filename: str, speed: float = 1.0, idle_time_limit: Optional[float] = None):
    """Replay a terminal session from a cast file."""
    if speed <= 0:
        raise ReplayError("Speed must be greater than 0")
    if idle_time_limit is not None and idle_time_limit < 0:
        raise ReplayError("Idle time limit must be zero or greater")

    try:
        records = read_records(filename)
        header = next(records)
    except FileNotFoundError as exc:
        raise ReplayError(f"File '{filename}' not found") from exc
    except ValueError as exc:
        raise ReplayError(str(exc)) from exc
    except StopIteration as exc:
        raise ReplayError("Empty file") from exc
    except OSError as exc:
        raise ReplayError(f"Error reading file: {exc}") from exc

    if not isinstance(header, AsciiCastV2Header):
        raise ReplayError("Invalid file format (missing header)")

    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()

    current_time = 0.0
    try:
        for record in records:
            if not isinstance(record, AsciiCastV2Event) or record.event_type != "o":
                continue

            delay = (record.time - current_time) / speed
            if idle_time_limit is not None and delay > idle_time_limit:
                delay = idle_time_limit
            if delay > 0:
                time.sleep(delay)

            sys.stdout.write(record.event_data)
            sys.stdout.flush()
            current_time = record.time
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError) as exc:
        raise ReplayError(f"Replay failed: {exc}") from exc
    finally:
        print()
