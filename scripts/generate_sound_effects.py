"""Procedural operation sounds for a video timeline (not music, no external SFX library).

Works with Python standard library. Generates key taps, mechanical wheel ticks,
and restrained icon motion/click cues. Visuals must be provided separately.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import struct
import wave
from array import array
from pathlib import Path

SR = 24000


def finite(value: float)->float:
    if not math.isfinite(value):raise ValueError('non-finite timestamp or gain')
    return value


def synth(out:Path,timeline:dict):
    length=finite(float(timeline['video_duration']))
    if not 0 < length <= 600:raise ValueError('Video length must be in (0,600] seconds')
    frames=round(length*SR)
    # A stereo float buffer, stored in arrays to avoid large Python-object lists.
    left=array('f',[0.0])*frames
    right=array('f',[0.0])*frames
    rng=random.Random(220613)
    foley=timeline['foley']
    cfg=timeline['cues']
    typing=float(cfg['typing_end'])
    scroll_begin=float(cfg['scroll_start']);scroll_end=float(cfg['scroll_end'])
    icon=float(cfg['icon_start']); reveal=float(cfg['reveal_start'])
    if not 0<=typing<=scroll_begin<=scroll_end<=icon<=reveal<=length:
        raise ValueError('Cues must follow typing_end <= scroll_start <= scroll_end <= icon_start <= reveal_start')
    def stamp(at:float,n:int,style:str,gain:float,pan:float=0):
        at=finite(float(at));gain=finite(float(gain))
        if gain<0 or gain>2:raise ValueError('foley gain out of range 0..2')
        start=round(at*SR)
        if start<0 or start>=frames:return
        end=min(n,frames-start)
        l=math.sqrt((1-max(-1,min(1,pan)))/2)*gain
        r=math.sqrt((1+max(-1,min(1,pan)))/2)*gain
        for k in range(end):
            t=k/SR
            if style=='key':
                signal=(.60*math.sin(2*math.pi*920*t)*math.exp(-128*t)
                       +.32*rng.uniform(-1,1)*math.exp(-195*t))
            elif style=='wheel':
                signal=(.33*math.sin(2*math.pi*470*t)*math.exp(-140*t)
                       +.28*rng.uniform(-1,1)*math.exp(-170*t))
            elif style=='click':
                signal=(.57*math.sin(2*math.pi*1220*t)*math.exp(-78*t)
                       +.22*rng.uniform(-1,1)*math.exp(-110*t))
            elif style=='woosh':
                duration=n/SR;u=t/duration
                signal=(.28*math.sin(2*math.pi*(290*t+330*t*t))
                      +.18*rng.uniform(-1,1))*math.sin(math.pi*u)**2
            else:raise ValueError(style)
            left[start+k]+=signal*l
            right[start+k]+=signal*r
    # Discrete mechanical keys, not a continuous arbitrary musical rhythm.
    keys=foley.get('typing_times',[])
    if not all(0<=float(x)<typing for x in keys):
        raise ValueError('typing_times must occur before typing_end')
    for i,t in enumerate(keys):stamp(float(t),round(.085*SR),'key',float(foley.get('keyboard_gain',.15)),(-.23 if i%2 else .21))
    # Scroll clicks only when the on-screen history actually scrolls.
    for i,t in enumerate(foley.get('scroll_times',[])):
        if not scroll_begin <= float(t)<scroll_end:raise ValueError('scroll_times must be within scroll window')
        stamp(float(t),round(.075*SR),'wheel',float(foley.get('wheel_gain',.15)),(-.12 if i%2 else .13))
    if foley.get('icon_whoosh',True):stamp(icon+.12,round(.55*SR),'woosh',float(foley.get('whoosh_gain',.045)),-.2)
    if foley.get('icon_click',True):
        click_at=float(foley.get('icon_click_at',icon+1.93))
        if not icon<=click_at<reveal:raise ValueError('icon_click_at must occur between icon_start and reveal_start')
        stamp(click_at,round(.10*SR),'click',float(foley.get('click_gain',.12)),.05)
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError(out)
    with wave.open(str(out),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        batch=8192
        for start in range(0,frames,batch):
            buf=bytearray()
            for i in range(start,min(start+batch,frames)):
                x=max(-.96,min(.96,left[i]));y=max(-.96,min(.96,right[i]))
                buf.extend(struct.pack('<hh',round(x*32767),round(y*32767)))
            w.writeframesraw(buf)
    print(f'Generated operation sounds: {out} | {length:.3f}s (no music)')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--timeline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    timeline=json.loads(a.timeline.read_text(encoding='utf-8'))
    synth(a.output.expanduser().resolve(),timeline)
if __name__=='__main__':main()
