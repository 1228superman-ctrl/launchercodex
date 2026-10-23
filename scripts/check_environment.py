"""Read-only inspection of FFmpeg and optional video/music inputs."""
from __future__ import annotations
import argparse
import json
import platform
import shutil
from pathlib import Path
from common import probe, choose_audio, choose_video


def main() -> None:
    p = argparse.ArgumentParser(description="Check tools and media, without changing files")
    p.add_argument("--video", type=Path)
    p.add_argument("--music", type=Path)
    a = p.parse_args()
    r = {"platform":platform.platform(), "python":platform.python_version(),
         "commands":{n:shutil.which(n) for n in ["ffmpeg","ffprobe","mpv","powershell","pwsh"]},
         "media": {}}
    for label, path in [("video",a.video),("music",a.music)]:
        if path:
            info=probe(path)
            r["media"][label] = {
                "path":str(path),"duration":float(info["format"]["duration"]),
                "video":choose_video(info),"audio":choose_audio(info)}
    print(json.dumps(r,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
