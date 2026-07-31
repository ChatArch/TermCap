"""Produce deterministic terminal output for the visual documentation example."""

import importlib.metadata
import sys
import time


RESET = "\033[0m"
BOLD_CYAN = "\033[1;36m"
GREEN = "\033[32m"
DIM = "\033[2m"


def line(text="", delay=0.24):
    print(text, flush=True)
    time.sleep(delay)


def status(text, delay=0.32):
    sys.stdout.write(f"\r  {BOLD_CYAN}›{RESET} {text:<28}")
    sys.stdout.flush()
    time.sleep(delay)


def main():
    version = importlib.metadata.version("termcap")
    line(f"{BOLD_CYAN}TermCap {version}{RESET}")
    line("Capture once, export twice.")
    line(delay=0.12)

    status("recording PTY")
    status("rendering animated SVG")
    status("encoding deterministic GIF")
    sys.stdout.write(f"\r  {GREEN}✓{RESET} SVG and GIF are ready.      \n")
    sys.stdout.flush()
    time.sleep(0.28)

    line("Wide text: Lean · 形式化数学", delay=0.28)
    line(f"{DIM}Ready to embed in your documentation.{RESET}", delay=0.1)


if __name__ == "__main__":
    main()
