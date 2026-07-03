#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rendu HTML -> PDF via navigateur (Playwright/Chromium).

Rendu fidèle de la charte (CSS complet). Usage : python3 html2pdf.py in.html out.pdf
Nécessite : pip install playwright + un Chromium (PLAYWRIGHT_BROWSERS_PATH).
"""
import glob
import os
import sys

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")

from playwright.sync_api import sync_playwright  # noqa: E402


def find_chrome():
    """Trouve un binaire Chromium installé, quelle que soit la révision."""
    env = os.environ.get("CHROME_BIN")
    if env and os.path.exists(env):
        return env
    patterns = [
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def main():
    src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    chrome = find_chrome()
    launch_kwargs = {"args": ["--no-sandbox", "--disable-gpu"]}
    if chrome:
        launch_kwargs["executable_path"] = chrome
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto("file://" + src, wait_until="networkidle")
        page.pdf(path=dst, format="A4",
                 margin={"top": "1.4cm", "bottom": "1.4cm", "left": "1.2cm", "right": "1.2cm"},
                 print_background=True)
        browser.close()
    print(f"PDF écrit : {dst}")


if __name__ == "__main__":
    main()
