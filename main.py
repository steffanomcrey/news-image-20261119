#!/usr/bin/env python3
"""news-image-20261119 entry (Python 3.13, standard library only).

The entry image is the front page in entry.png, drawn by render.py in this
repository. This program copies it to /output/entry.png, so both graded runs
write the same bytes. No network is used.

Local run:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
from pathlib import Path

SRC = Path(__file__).with_name("entry.png")
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"

OUT.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, OUT)
