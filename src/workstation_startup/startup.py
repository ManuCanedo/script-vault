#!/usr/bin/env python3

import asyncio
import os
import subprocess
import time
import webbrowser


def open_terminals():
    delay = 0.2
    screen_info = (
        subprocess.check_output("xrandr | grep '*' | awk '{print $1}'", shell=True)
        .decode()
        .strip()
    )
    screen_width, screen_height = map(int, screen_info.split("x"))

    t1 = subprocess.Popen(["gnome-terminal"])
    time.sleep(delay)  # Allow time for the window to open
    subprocess.run(
        ["wmctrl", "-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"]
    )
    subprocess.run(
        ["wmctrl", "-r", ":ACTIVE:", "-e", f"0,0,0,{screen_width//2},{screen_height}"]
    )

    t2 = subprocess.Popen(["gnome-terminal"])
    time.sleep(delay)  # Allow time for the window to open
    subprocess.run(
        ["wmctrl", "-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"]
    )
    subprocess.run(
        [
            "wmctrl",
            "-r",
            ":ACTIVE:",
            "-e",
            f"0,{screen_width//2},0,{screen_width//2},{screen_height}",
        ]
    )


async def open_chrome_tabs(urls):
    for url in urls:
        webbrowser.open_new_tab(url)


async def open_slack():
    await asyncio.create_subprocess_exec("slack")


async def open_vscode(path):
    await asyncio.create_subprocess_exec("code", path)


async def main():
    open_terminals()

    await asyncio.gather(
        open_vscode(os.path.expanduser("~/dev/firmware")),
        open_slack(),
        open_chrome_tabs(
            [
                "https://chat.openai.com/chat",
                "https://gitlab.eng.roku.com/firmware/firmware/-/merge_requests?scope=all&state=merged&author_username=mtabares",
                "https://jira.portal.roku.com:8443/secure/Dashboard.jspa?",
            ]
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
