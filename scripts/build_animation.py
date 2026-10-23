"""Normalize and concatenate user-supplied VIDEO clips. Does NOT generate art or music."""
from __future__ import annotations
import argparse
import tempfile
from pathlib import Path
from common import tool, run, duration, validate_new_output


def normalize(clips: list[Path], path: Path, width: int, height: int, fps: int):
    if len(clips)<1: raise ValueError('At least one supplied video clip is required')
    for c in clips:
        if not c.is_file():raise FileNotFoundError(c)
    if fps<15 or fps>60:raise ValueError('fps must be 15..60')
    if width%2 or height%2 or min(width,height)<240:raise ValueError('even W/H >=240 required')
    out=validate_new_output(path, clips)
    with tempfile.TemporaryDirectory(prefix='codex-anime-') as tmp:
        t=Path(tmp);names=[]
        filt=f'scale={width}:{height}:force_original_aspect_ratio=decrease,' \
             f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,' \
             f'setsar=1,fps={fps},format=yuv420p'
        for n,c in enumerate(clips):
            normalized=t/f'{n:03d}.mp4'
            run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(c),
                 '-vf',filt,'-an','-c:v','libx264','-preset','fast','-crf','20',
                 '-pix_fmt','yuv420p','-r',str(fps),str(normalized)])
            names.append(normalized)
        listing=t/'concat.txt'
        # These are predictable auto-generated names under a temporary directory.
        listing.write_text(''.join("file '"+f.as_posix().replace("'", "'\\''")+"'\n" for f in names),encoding='utf-8')
        run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y',
             '-f','concat','-safe','0','-i',str(listing),'-c','copy',
             '-movflags','+faststart',str(out)])
    print(f'Video assembled: {out} | {duration(out):.3f}s')
    return out


def portrait(input_video: Path, output: Path, fps: int):
    result=validate_new_output(output,[input_video])
    filterv=('split=2[bb][ff];[bb]scale=1080:1920:force_original_aspect_ratio=increase,'
             'crop=1080:1920,boxblur=28:9,eq=brightness=-0.25:saturation=0.6[bg];'
             '[ff]scale=1080:-2,setsar=1[fg];'
             '[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[v]')
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(input_video),
         '-filter_complex',filterv,'-map','[v]','-an','-r',str(fps),
         '-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(result)])
    print(f'Portrait assembled: {result}')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--clips',required=True,nargs='+',type=Path,help='Input video segments in order')
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--width',type=int,default=1280)
    p.add_argument('--height',type=int,default=720)
    p.add_argument('--fps',type=int,default=24)
    p.add_argument('--portrait-output',type=Path,help='Optional blurred-backdrop portrait version')
    a=p.parse_args()
    vid=normalize(a.clips,a.output,a.width,a.height,a.fps)
    if a.portrait_output:portrait(vid,a.portrait_output,a.fps)
if __name__=='__main__':main()
