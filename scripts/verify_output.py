"""Playback/format checks, phase loudness report, and picture bitstream comparison."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from common import tool, run, probe, choose_audio, choose_video


def videohash(path:Path)->str:
    return run([tool('ffmpeg'),'-v','error','-i',str(path),'-map','0:v:0',
                '-c:v','copy','-f','hash','-hash','SHA256','-'],get_output=True).strip()


def loudness(path:Path,a:float,b:float)->dict:
    if b<=a:return {'mean_dB':None,'peak_dB':None}
    # volumedetect writes its measurements to stderr.
    import subprocess
    r=subprocess.run([tool('ffmpeg'),'-hide_banner','-nostats','-ss',str(a),
         '-t',str(b-a),'-i',str(path),'-vn','-af','volumedetect','-f','null','-'],
         stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stderr[-1000:])
    def val(name):
        m=re.search(name+r':\s*(-?\d+(?:\.\d+)?) dB',r.stderr)
        return float(m.group(1)) if m else None
    return {'mean_dB':val('mean_volume'),'peak_dB':val('max_volume')}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--video',required=True,type=Path)
    a.add_argument('--timeline',type=Path)
    a.add_argument('--compare-video-to',type=Path,help='Verify identical video bitstream against a source')
    a.add_argument('--report',type=Path,help='Write JSON report')
    ns=a.parse_args();p=ns.video
    info=probe(p);v=choose_video(info);au=choose_audio(info)
    if not v or not au:raise RuntimeError('Missing video or audio stream')
    real=float(info['format']['duration'])
    run([tool('ffmpeg'),'-v','error','-i',str(p),'-f','null','-'])
    report={'video':str(p),'duration_seconds':round(real,3),
            'width':v.get('width'),'height':v.get('height'),
            'video_codec':v.get('codec_name'),'audio_codec':au.get('codec_name'),
            'full_decode':'pass'}
    if ns.compare_video_to:
        matching=videohash(p)==videohash(ns.compare_video_to)
        report['picture_bitstream_unchanged']=matching
        if not matching:raise RuntimeError('Video bitstream differs from input')
    if ns.timeline:
        c=json.loads(ns.timeline.read_text(encoding='utf8'))
        target=float(c['video_duration'])
        if abs(real-target)>.15:raise RuntimeError('Duration mismatch with timeline')
        cues=c['cues'];times=[('typing',0,float(cues['typing_end'])),
             ('scroll',float(cues['scroll_start']),float(cues['scroll_end'])),
             ('icon',float(cues['icon_start']),float(cues['reveal_start'])),
             ('music_early',float(cues['reveal_start'])+.15,
                  min(float(cues['reveal_start'])+1.15,real)),
             ('music_late',max(float(cues['theme_start'])-1.3,float(cues['reveal_start'])),
                  float(cues['theme_start'])),
             ('outro',float(cues['theme_start']),real)]
        report['phases']={name:loudness(p,start,end) for name,start,end in times}
        # Preserve diagnostic measurements rather than false claims of 'no music'
        # based on loudness alone. Only the mix design guarantees separation.
    if ns.report:
        ns.report.parent.mkdir(parents=True,exist_ok=True)
        ns.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
