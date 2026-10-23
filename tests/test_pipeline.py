"""Integration test with synthetic non-copyright media only.

This generates simple technical test patterns, never anime/stock/user imagery.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


def cli(*args):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                            capture_output=True, text=True, timeout=240)
    if result.returncode:
        raise AssertionError(f'Command failed: {args}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def ff(*args):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *map(str, args)],
                            capture_output=True, text=True, timeout=240)
    if result.returncode:
        raise AssertionError(result.stderr)


def probe(path):
    result = subprocess.run(['ffprobe','-v','error','-show_entries',
                             'format=duration:stream=codec_type,width,height,r_frame_rate',
                             '-of','json',str(path)],capture_output=True,text=True,check=True,timeout=30)
    return json.loads(result.stdout)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg not installed')
class PipelineTest(unittest.TestCase):
    def test_30fps_media_audio_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            a,b=d/'a.mp4',d/'b.mp4'
            ff('-f','lavfi','-i','color=c=black:s=640x360:r=30:d=0.8',
               '-an','-c:v','libx264','-pix_fmt','yuv420p',a)
            ff('-f','lavfi','-i','color=c=white:s=640x360:r=30:d=0.8',
               '-an','-c:v','libx264','-pix_fmt','yuv420p',b)
            vid,vertical=d/'master.mp4',d/'portrait.mp4'
            cli(SCRIPTS/'build_animation.py','--clips',a,b,'--output',vid,
                '--portrait-output',vertical,'--fps',30,'--width',640,'--height',360)
            info=probe(vid)
            duration=float(info['format']['duration'])
            self.assertAlmostEqual(duration,1.6,delta=.11)
            self.assertEqual(next(s for s in info['streams'] if s['codec_type']=='video')['r_frame_rate'],'30/1')
            verticalInfo=probe(vertical)
            vs=next(s for s in verticalInfo['streams'] if s['codec_type']=='video')
            self.assertEqual(vs['r_frame_rate'],'30/1')
            self.assertEqual((vs['width'],vs['height']),(1080,1920))
            cues={"typing_end":.2,"scroll_start":.2,"scroll_end":.5,
                  "icon_start":.5,"reveal_start":.9,"theme_start":1.30}
            timeline={"video_duration":duration,"cues":cues,
                      "foley":{"typing_times":[.04,.11],"scroll_times":[.29,.38],
                      "icon_click_at":.73,"wheel_gain":.06},
                      "music":{"song_offset_seconds":.2,"start_gain":.09,
                               "rise_gain":.65,"rise_seconds":.4,
                               "outro_seconds":duration-1.30}}
            times=d/'timeline.json';times.write_text(json.dumps(timeline))
            sound=d/'foley.wav'
            cli(SCRIPTS/'generate_sound_effects.py','--timeline',times,'--output',sound)
            song=d/'my_music.wav'
            ff('-f','lavfi','-i','sine=frequency=440:duration=2.5:sample_rate=48000',song)
            mix=d/'music.mp4'
            cli(SCRIPTS/'sync_music.py','--video',vid,'--foley',sound,
                '--music',song,'--timeline',times,'--output',mix)
            report=d/'report.json'
            cli(SCRIPTS/'verify_output.py','--video',mix,'--compare-video-to',vid,
                '--timeline',times,'--report',report)
            check=json.loads(report.read_text())
            self.assertTrue(check['picture_bitstream_unchanged'])
            self.assertEqual(check['full_decode'],'pass')
            self.assertIn('music_late',check['phases'])
            self.assertAlmostEqual(float(probe(mix)['format']['duration']),duration,delta=.13)
            # No-music run uses a separate output and must not require a song.
            nomusic=d/'no_music.mp4'
            cli(SCRIPTS/'sync_music.py','--video',vid,'--foley',sound,
                '--timeline',times,'--output',nomusic)
            self.assertEqual(json.loads(cli(SCRIPTS/'verify_output.py','--video',nomusic,
                        '--compare-video-to',vid))['full_decode'],'pass')
            # Existing output must not be modified or overwritten.
            with self.assertRaises(AssertionError):
                cli(SCRIPTS/'build_animation.py','--clips',a,b,'--output',vid)

    def test_bad_timeline_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            config={'video_duration':2,'cues':{'typing_end':1,'scroll_start':1,
                    'scroll_end':.9,'icon_start':1.2,'reveal_start':1.5},'foley':{}}
            timeline=d/'bad.json';timeline.write_text(json.dumps(config))
            with self.assertRaises(AssertionError):
                cli(SCRIPTS/'generate_sound_effects.py','--timeline',timeline,
                    '--output',d/'bad.wav')

if __name__=='__main__':
    unittest.main()
