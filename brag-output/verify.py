"""Verify the exported film contract without touching the application."""
from pathlib import Path
import json, subprocess
root=Path(__file__).resolve().parent
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(root/'brag.mp4')]))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (video['width'],video['height'])==(1920,1080)
assert video['r_frame_rate']=='30/1'
assert int(video['nb_frames'])==750
assert abs(float(probe['format']['duration'])-25)<0.04
assert abs(float(audio['duration'])-25)<0.04
assert (root/'brag.jpg').stat().st_size>10000
assert (root/'wristcue-icon.png').stat().st_size>10000
assert json.loads((root/'check-final.json').read_text())['ok']
print('PASS: 1920×1080, 30 fps, 750 frames, 25 seconds, audio present, poster/icon present, Hyperframes check passed.')
