"""Build the V13-style soundtrack from a foley WAV and a USER-PROVIDED music file.

The source video's audio is *never* included. Existing tracks cannot leak back
into scroll/icon scenes. Works for any duration when cues in JSON are updated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from common import tool, run, probe, choose_audio, choose_video, validate_new_output


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--video',type=Path,required=True,help='Picture/video input; its audio is discarded')
    ap.add_argument('--foley',type=Path,required=True,help='Full-length WAV from generate_sound_effects.py')
    ap.add_argument('--music',type=Path,help='Licensed/user-provided music; no music when omitted')
    ap.add_argument('--timeline',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    c=json.loads(args.timeline.read_text(encoding='utf-8'))
    expected=float(c['video_duration'])
    vs=probe(args.video)
    if not choose_video(vs):raise ValueError('video input has no video stream')
    real=float(vs['format']['duration'])
    if abs(real-expected)>.2:raise ValueError(f'timeline expects {expected}s but video is {real:.3f}s; recalibrate cues')
    fs=probe(args.foley)
    if not choose_audio(fs) or abs(float(fs['format']['duration'])-expected)>.2:
        raise ValueError('Foley WAV must be full-length and aligned to video')
    cfg=c['music'];on=float(c['cues']['reveal_start'])
    off=float(c['cues']['theme_start'])
    if not 0<=on<off<=expected:raise ValueError('invalid music cue windows')
    fade_len=float(cfg.get('rise_seconds',off-on))
    ending=float(cfg.get('outro_seconds',expected-off))
    baseline=float(cfg.get('start_gain',.09));rise=float(cfg.get('rise_gain',.65))
    offset=float(cfg.get('song_offset_seconds',0))
    for x in [fade_len,ending,baseline,rise,offset]:
        if x<0:raise ValueError('negative music setting')
    if fade_len<=0 or ending<=0:raise ValueError('rise_seconds and outro_seconds must be >0')
    if fade_len>off-on+.15:raise ValueError('music rise exceeds reveal window')
    if ending>expected-off+.15:raise ValueError('music outro exceeds ending window')
    if baseline+rise>1.5:raise ValueError('baseline+rise gain above 1.5; review mix')
    out=validate_new_output(args.output,[args.video,args.foley]+([args.music] if args.music else []))
    argsff=[tool('ffmpeg'),'-hide_banner','-loglevel','error','-n',
            '-i',str(args.video),'-i',str(args.foley)]
    if args.music:
        ms=probe(args.music)
        if not choose_audio(ms):raise ValueError('music file has no audio')
        wanted=expected-on
        if float(ms['format']['duration']) < offset+wanted-.08:
            raise ValueError('music does not contain enough seconds after song_offset_seconds')
        argsff+=['-i',str(args.music)]
        # At reveal_begin music starts quietly; it climbs until full character
        # reveal and fades out throughout the actual final Codex UI scene.
        filt=(
          '[1:a]aresample=48000,aformat=channel_layouts=stereo[sfx];'
          f'[2:a]atrim=start={offset:.6f}:duration={wanted:.6f},'
          'asetpts=PTS-STARTPTS,aresample=48000,'
          'aformat=channel_layouts=stereo,asplit=2[m0][m1];'
          f'[m0]volume={baseline:.6f}[soft];'
          f'[m1]afade=t=in:st=0:d={fade_len:.6f}:curve=tri,'
          f'volume={rise:.6f}[rising];'
          '[soft][rising]amix=inputs=2:duration=first:normalize=0,'
          f'afade=t=out:st={off-on:.6f}:d={ending:.6f},'
          f'adelay={round(on*1000)}:all=1[music];'
          f'[sfx][music]amix=inputs=2:duration=first:normalize=0,'
          f'alimiter=limit=0.95:attack=5:release=80:level=false,atrim=0:{expected:.6f}[out]')
    else:
        filt=f'[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{expected:.6f}[out]'
    argsff+=['-filter_complex',filt,'-map','0:v:0','-map','[out]','-c:v','copy',
             '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
             '-movflags','+faststart','-shortest',str(out)]
    run(argsff)
    info=probe(out)
    if not choose_video(info) or not choose_audio(info):raise RuntimeError('output missing a stream')
    print(f'Created: {out} | {info["format"]["duration"]}s | picture copied without re-encoding')

if __name__=='__main__':main()
