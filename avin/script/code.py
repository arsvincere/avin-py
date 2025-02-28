#!/usr/bin/env  python3

import asyncio
from datetime import date

from avin import *


async def main():
    calcProjectRows()


def calcProjectRows():
    code_dir = "avin"
    gui_dir = "gui"
    test_dir = "tests"
    usr_str = "usr/strategy"
    usr_lib = "usr/lib"
    usr_util = "usr/utils"

    start = date(2023, 7, 23)
    dt = date.today()

    code_files, code_str = code_counter(code_dir)
    gui_files, gui_str = code_counter(gui_dir)
    test_files, test_str = code_counter(test_dir)
    strt_files, strt_str = code_counter(usr_str)
    anal_files, anal_str = code_counter(usr_lib)
    util_files, util_str = code_counter(usr_util)

    total_files = (
        code_files
        + gui_files
        + test_files
        + strt_files
        + anal_files
        + util_files
    )
    total_str = code_str + gui_str + test_str + strt_str + anal_str + util_str
    days = (dt - start).days
    row_per_day = int(total_str / days)

    print(f"{'':-<78}")
    print(f"{'Code':<12} | {code_files:>12} | {code_str:>13} | ")
    print(f"{'Gui':<12} | {gui_files:>12} | {gui_str:>13} | ")
    print(f"{'Pytest':<12} | {test_files:>12} | {test_str:>13} | ")
    print(f"{'Strategy':<12} | {strt_files:>12} | {strt_str:>13} | ")
    print(f"{'User lib':<12} | {anal_files:>12} | {anal_str:>13} | ")
    print(f"{'Utils':<12} | {util_files:>12} | {util_str:>13} | ")
    print(f"{'':-<78}")
    print(
        f"{dt}   | "
        f"files {total_files:>6} | "
        f"rows {total_str:>8} | "
        f"days {days:>6} | "
        f"rows/day {row_per_day:>5}"
    )
    print(f"{'':-<78}")


if __name__ == "__main__":
    asyncio.run(main())
