#!/usr/bin/env  python3

import asyncio
from collections import defaultdict

from avin import *

ALL_TIME = defaultdict(TimeDelta)


async def main():
    journal_file = "/home/alex/diary/journal/journal.un"
    calc_time(journal_file)


def calc_time(file_path: str):  # {{{
    text = Cmd.loadText(file_path)
    time_lines = list()
    for line in text:
        # if line.startswith("= "):
        #     dt = line.split(" ")[1].strip()
        #     dt = Date.fromisoformat(dt)

        if line.startswith("== Time"):
            time_lines.clear()
        if line.startswith("    "):
            time_lines.append(line)
        if line == "\n":
            process_time_lines(time_lines)

    for tag, time in ALL_TIME.items():
        hours = time.total_seconds() / 60 / 60
        print(f"{tag:<10} {hours:>5.1f}")


# }}}
def process_time_lines(time_lines: list[str]):  # {{{
    for line in time_lines:
        time, tag = process_line(line)
        ALL_TIME[tag] += time


# }}}
def process_line(line: str):  # {{{
    time_str, tag = line.split()

    hours, minutes = time_str.split(":")
    time = TimeDelta(hours=int(hours), minutes=int(minutes))

    return time, tag


# }}}

if __name__ == "__main__":
    asyncio.run(main())
