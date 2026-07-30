"""Core recording logic"""
import os
import pty
import select
import time
import fcntl
import termios
import struct
import codecs
from typing import Iterator, List, Union

from termcap.parser.asciicast import AsciiCastV2Header, AsciiCastV2Event

def record_session(
    process_args: List[str],
    columns: int,
    lines: int,
    input_fileno: int,
    output_fileno: int
) -> Iterator[Union[AsciiCastV2Header, AsciiCastV2Event]]:
    """Record a terminal session"""
    
    # Yield the header first
    yield AsciiCastV2Header(
        version=2,
        width=columns,
        height=lines,
        timestamp=int(time.time())
    )

    pid, master_fd = pty.fork()
    
    if pid == 0:
        # Child process
        os.execvp(process_args[0], process_args)
        
    # Parent process
    # Set terminal size for the PTY
    winsize = struct.pack("HHHH", lines, columns, 0, 0)
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
    
    # Use incremental decoder to handle multi-byte characters split across chunks
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
    
    start_time = time.time()
    stdin_open = True
    master_open = True
    child_exited = False

    try:
        while master_open:
            read_fds = [master_fd]
            if stdin_open:
                read_fds.append(input_fileno)

            try:
                ready, _, _ = select.select(read_fds, [], [], 0.1)
            except InterruptedError:
                continue

            if stdin_open and input_fileno in ready:
                try:
                    data = os.read(input_fileno, 1024)
                except OSError:
                    data = b""
                if data:
                    os.write(master_fd, data)
                else:
                    # Command-mode recording often starts with stdin already at
                    # EOF. Stop polling it so the PTY output cannot be starved.
                    stdin_open = False

            if master_fd in ready:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    # Linux PTYs commonly report EIO after the child exits and
                    # all buffered output has been drained.
                    master_open = False
                    continue

                if not data:
                    master_open = False
                    continue

                os.write(output_fileno, data)
                elapsed = time.time() - start_time
                decoded_data = decoder.decode(data, final=False)
                if decoded_data:
                    yield AsciiCastV2Event(
                        time=elapsed,
                        event_type="o",
                        event_data=decoded_data,
                    )

            if not child_exited:
                try:
                    waited_pid, _ = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    child_exited = True
                else:
                    child_exited = waited_pid == pid

            # Do not break when the child exits: the PTY may still contain its
            # final output. The loop ends only after master_fd reaches EOF/EIO.
    finally:
        os.close(master_fd)
        if not child_exited:
            try:
                os.waitpid(pid, 0)
            except (ChildProcessError, OSError):
                pass

        remaining = decoder.decode(b"", final=True)
        if remaining:
            yield AsciiCastV2Event(
                time=time.time() - start_time,
                event_type="o",
                event_data=remaining,
            )
