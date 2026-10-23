"""Shared, dependency-free FFmpeg helpers for the Codex Anime Launcher skill."""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path


def tool(name: str) -> str:
    loc = shutil.which(name)
    if not loc:
        raise RuntimeError(f"Cannot find {name}. Install FFmpeg and put its bin directory on PATH.")
    return loc


def run(args: list[str], *, get_output: bool = False) -> str:
    p = subprocess.run(args, text=True, encoding="utf-8", errors="replace",
                       stdout=subprocess.PIPE if get_output else subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("Command failed: " + ' '.join(map(str,args[:5])) + "\n" + p.stderr[-4000:])
    return p.stdout if get_output else ""


def probe(path: str | Path) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(run([tool("ffprobe"), "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", str(p)], get_output=True))


def duration(path: str | Path) -> float:
    return float(probe(path)["format"]["duration"])


def validate_new_output(output: str | Path, inputs: list[str | Path]) -> Path:
    p = Path(output).expanduser().resolve()
    inpaths = [Path(s).expanduser().resolve() for s in inputs]
    if p in inpaths:
        raise ValueError("Output must not overwrite a source file.")
    if p.exists():
        raise FileExistsError(f"Output already exists (not overwriting): {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def choose_video(info: dict) -> dict:
    return next((s for s in info["streams"] if s["codec_type"] == "video"), None)


def choose_audio(info: dict) -> dict:
    return next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
