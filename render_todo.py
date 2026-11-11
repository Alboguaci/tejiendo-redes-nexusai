"""
Script de renderizado maestro para la sustentación completa de la Actividad 4:
'Tejiendo Redes: Arquitectura de software entre hilos y nodos' - NexusAI 2.0.

Ensambla los 22 turnos (Juan Carlos Benítez Rojas & Juan José Córdoba Eraso),
agrega cortinilla de entrada (4s) y créditos finales (6s),
aplica normalización de audio EBU R128 y genera el video final en Full HD 1080p.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIDEO_DIR = ROOT / "video_sustentacion"
CRUDOS_DIR = VIDEO_DIR / "crudos"
SLIDES_DIR = VIDEO_DIR / "slides"
SEGMENTOS_DIR = VIDEO_DIR / "segmentos"
SEGMENTOS_DIR.mkdir(parents=True, exist_ok=True)

FINAL_OUTPUT = VIDEO_DIR / "Sustentacion_NexusAI2_Actividad4_16min.mp4"

def run_cmd(cmd, desc=""):
    print(f"\n--- {desc} ---")
    start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    if res.returncode != 0:
        print(f"ERROR ({elapsed:.1f}s):\n{res.stderr[-600:]}")
        sys.exit(1)
    else:
        print(f"OK ({elapsed:.1f}s)")
    return res

def render_intro():
    intro_img = SLIDES_DIR / "intro.png"
    intro_out = SEGMENTOS_DIR / "intro.mp4"
    if intro_out.exists() and intro_out.stat().st_size > 100000:
        print("Intro ya existe, omitiendo...")
        return intro_out
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "4.0", "-i", str(intro_img),
        "-f", "lavfi", "-t", "4.0", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex", "[0:v]fade=t=in:st=0:d=1,format=yuv420p[v_out]",
        "-map", "[v_out]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(intro_out)
    ]
    run_cmd(cmd, "Renderizando Cortinilla de Entrada (4s)")
    return intro_out

def render_outro():
    outro_img = SLIDES_DIR / "outro.png"
    outro_out = SEGMENTOS_DIR / "outro.mp4"
    if outro_out.exists() and outro_out.stat().st_size > 100000:
        print("Outro ya existe, omitiendo...")
        return outro_out
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "6.0", "-i", str(outro_img),
        "-f", "lavfi", "-t", "6.0", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex", "[0:v]fade=t=out:st=4:d=2,format=yuv420p[v_out]",
        "-map", "[v_out]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(outro_out)
    ]
    run_cmd(cmd, "Renderizando Créditos Finales (6s)")
    return outro_out

def render_segment(turn_idx: int):
    turn_str = f"{turn_idx:02d}"
    slide_file = SLIDES_DIR / f"slide_{turn_str}.png"
    
    # Buscar el crudo correspondiente
    crudo_candidates = list(CRUDOS_DIR.glob(f"T{turn_str}_*.mp4"))
    if not crudo_candidates:
        raise FileNotFoundError(f"No se encontró crudo para turno {turn_str}")
    crudo_file = crudo_candidates[0]
    
    seg_out = SEGMENTOS_DIR / f"segment_{turn_str}.mp4"
    if seg_out.exists() and seg_out.stat().st_size > 500000:
        print(f"Segmento {turn_str} ya existe ({seg_out.stat().st_size/1024/1024:.2f} MB), omitiendo...")
        return seg_out
    
    filter_complex = (
        "[1:v]scale=424:755[v_cam];"
        "[0:v][v_cam]overlay=x=1408:y=175:shortest=1,format=yuv420p[v_out];"
        "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a_out]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(slide_file),
        "-i", str(crudo_file),
        "-filter_complex", filter_complex,
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest",
        str(seg_out)
    ]
    speaker = "Juan Carlos" if "_JC" in crudo_file.name else "Juan José"
    run_cmd(cmd, f"Renderizando Turno {turn_str}/22 ({speaker} - {crudo_file.name})")
    return seg_out

def concat_all(segment_files):
    concat_list_file = SEGMENTOS_DIR / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for seg in segment_files:
            # En ffmpeg concat demuxer, se recomienda rutas absolutas o relativas con barras normales
            p_str = seg.resolve().as_posix()
            f.write(f"file '{p_str}'\n")
    
    print(f"\nLista de concatenación guardada en {concat_list_file}")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(FINAL_OUTPUT)
    ]
    run_cmd(cmd, f"Concatenando Video Maestro Final -> {FINAL_OUTPUT.name}")

def verify_final():
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json",
        str(FINAL_OUTPUT)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("\n================ VERIFICACIÓN TÉCNICA DEL VIDEO MAESTRO ================")
    print(res.stdout)
    if FINAL_OUTPUT.exists():
        size_mb = FINAL_OUTPUT.stat().st_size / (1024 * 1024)
        print(f"Archivo generado con éxito: {FINAL_OUTPUT}")
        print(f"Tamaño total: {size_mb:.2f} MB")
    print("========================================================================\n")

def main():
    print("Iniciando pipeline de producción audiovisual NexusAI 2.0...")
    total_start = time.time()
    
    # 1. Intro
    intro_seg = render_intro()
    
    # 2. 22 Segmentos
    segments = []
    for i in range(1, 23):
        seg = render_segment(i)
        segments.append(seg)
        
    # 3. Outro
    outro_seg = render_outro()
    
    # 4. Concatenación
    all_files = [intro_seg] + segments + [outro_seg]
    concat_all(all_files)
    
    # 5. Verificación
    verify_final()
    
    total_elapsed = time.time() - total_start
    print(f"¡PRODUCCIÓN FINALIZADA EN {total_elapsed/60:.2f} MINUTOS!")

if __name__ == "__main__":
    main()
