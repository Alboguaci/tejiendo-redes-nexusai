import os, subprocess, json
from pathlib import Path

downloads = Path(r"C:\Users\Admin\Downloads")
audio_dir = Path(r"Actividad4_Tejiendo_Redes\audio_samples")
audio_dir.mkdir(exist_ok=True)

# 1. PTV files (Juan Carlos)
ptv_files = sorted(list(downloads.glob("WhatsApp Ptv*.mp4")), key=lambda x: x.name)
# 2. Video files (Juan Jose)
video_files = sorted(list(downloads.glob("WhatsApp Video*.mp4")), key=lambda x: x.name)

print(f"Extracting audio samples: {len(ptv_files)} PTV, {len(video_files)} Video")

for i, f in enumerate(ptv_files):
    out_wav = audio_dir / f"jc_{i+1:02d}.wav"
    if not out_wav.exists():
        cmd = ["ffmpeg", "-y", "-i", str(f), "-t", "8", "-ar", "16000", "-ac", "1", str(out_wav)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for i, f in enumerate(video_files):
    # safe name
    safe_name = f.stem.replace("WhatsApp Video 2026-11-10 at ", "").replace(" ", "_")
    out_wav = audio_dir / f"jj_raw_{i+1:02d}_{safe_name}.wav"
    if not out_wav.exists():
        cmd = ["ffmpeg", "-y", "-i", str(f), "-t", "8", "-ar", "16000", "-ac", "1", str(out_wav)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Audio samples extracted successfully.")
