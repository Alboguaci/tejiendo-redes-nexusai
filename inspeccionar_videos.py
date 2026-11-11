import os, json, subprocess
from pathlib import Path

downloads = Path(r"C:\Users\Admin\Downloads")
video_exts = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

files = [f for f in downloads.iterdir() if f.suffix.lower() in video_exts]
# Sort by modification/creation time or name
files.sort(key=lambda x: x.name)

print(f"Total video files found: {len(files)}")
results = []

for f in files:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(f)
    ]
    try:
        out = subprocess.check_output(cmd, text=True)
        data = json.loads(out)
        fmt = data.get("format", {})
        duration = float(fmt.get("duration", 0.0))
        size_mb = f.stat().st_size / (1024 * 1024)
        
        v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        a_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
        
        w = v_stream.get("width", 0)
        h = v_stream.get("height", 0)
        fps = v_stream.get("r_frame_rate", "N/A")
        v_codec = v_stream.get("codec_name", "N/A")
        a_codec = a_stream.get("codec_name", "N/A")
        
        results.append({
            "name": f.name,
            "path": str(f),
            "duration": duration,
            "size_mb": round(size_mb, 2),
            "res": f"{w}x{h}",
            "fps": fps,
            "v_codec": v_codec,
            "a_codec": a_codec,
            "has_audio": bool(a_stream),
            "mtime": f.stat().st_mtime
        })
    except Exception as e:
        results.append({"name": f.name, "error": str(e)})

for r in results:
    dur = r.get("duration", 0)
    print(f"{r['name']}: {dur:.1f}s ({dur/60:.2f}m) | {r.get('res')} | {r.get('v_codec')}/{r.get('a_codec')} | {r.get('size_mb')}MB")

total_dur = sum(r.get("duration", 0) for r in results)
print("=" * 60)
print(f"Total combined duration: {total_dur:.1f}s ({total_dur/60:.2f} min)")
