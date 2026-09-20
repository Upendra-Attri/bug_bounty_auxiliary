#!/usr/bin/env python3

import os
import json
import time
import signal
import sys
from datetime import datetime

from pyfiglet import figlet_format


SAVE_FILE = "bug_hunting_time.json"

# Green terminal text
GREEN = "\033[92m"
RESET = "\033[0m"

# Hide cursor
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def clear_screen():
    os.system("clear")


def load_time():
    if not os.path.exists(SAVE_FILE):
        return 0

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        return int(data.get("elapsed_seconds", 0))

    except (json.JSONDecodeError, ValueError, TypeError):
        return 0


def save_time(seconds):
    data = {
        "elapsed_seconds": seconds,
        "hours": seconds // 3600,
        "minutes": (seconds % 3600) // 60,
        "seconds": seconds % 60
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def center_text(text, width):
    return text.center(width)


def draw_timer(elapsed):
    clear_screen()

    # Get terminal size
    width, height = os.get_terminal_size()

    # Current date
    date = datetime.now().strftime("%Y-%m-%d")

    # Big timer
    timer = format_time(elapsed)

    # Create large ASCII digits
    big_timer = figlet_format(
        timer,
        font="big"
    )

    lines = big_timer.rstrip("\n").split("\n")

    # Calculate vertical position
    date_row = max(2, height // 2 - 7)

    # Move cursor
    print(f"\033[{date_row};1H")

    # Date
    print(
        GREEN +
        center_text(date, width) +
        RESET
    )

    print()

    # Big timer
    for line in lines:
        print(
            GREEN +
            center_text(line, width) +
            RESET
        )

    # Bottom information
    print(f"\033[{height - 2};1H")
    print(
        center_text("BUG HUNTING TIMER  •  CTRL+C TO STOP", width)
    )


def cleanup():
    print(SHOW_CURSOR + RESET)
    clear_screen()


def stop_handler(signum, frame):
    global current_time

    save_time(current_time)

    cleanup()

    print(f"Saved bug-hunting time: {format_time(current_time)}")
    print(f"Saved to: {SAVE_FILE}")

    sys.exit(0)


# Handle Ctrl+C
signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)


# Start
previous_time = load_time()

# Hide cursor
print(HIDE_CURSOR, end="")

# Make sure cursor comes back if something goes wrong
try:

    start = time.monotonic()

    while True:

        current_time = previous_time + int(
            time.monotonic() - start
        )

        draw_timer(current_time)

        # Save every 10 seconds
        if current_time % 10 == 0:
            save_time(current_time)

        time.sleep(1)

except KeyboardInterrupt:
    stop_handler(None, None)

finally:
    cleanup()
