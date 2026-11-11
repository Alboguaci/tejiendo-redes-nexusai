"""Genera las cortinillas de introducción y créditos finales para el video maestro."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SLIDES_DIR = ROOT / "video_sustentacion" / "slides"
SLIDES_DIR.mkdir(parents=True, exist_ok=True)

FONT_TITLE_PATH = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REGULAR_PATH = r"C:\Windows\Fonts\segoeui.ttf"
FONT_MONO_PATH = r"C:\Windows\Fonts\consola.ttf"

def get_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

F_HERO = get_font(FONT_TITLE_PATH, 44)
F_TITLE = get_font(FONT_TITLE_PATH, 34)
F_SUBTITLE = get_font(FONT_REGULAR_PATH, 24)
F_BODY = get_font(FONT_REGULAR_PATH, 20)
F_BODY_BOLD = get_font(FONT_TITLE_PATH, 21)
F_SMALL = get_font(FONT_REGULAR_PATH, 16)
F_BADGE = get_font(FONT_TITLE_PATH, 15)

BG_COLOR = (11, 17, 32)
CARD_BG = (15, 23, 42)
CARD_BORDER = (51, 65, 85)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
TEXT_CYAN = (56, 189, 248)
TEXT_GREEN = (52, 211, 153)
TEXT_AMBER = (251, 191, 36)

def generate_intro():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    d = ImageDraw.Draw(img)

    # Marco central
    d.rounded_rectangle([100, 80, 1820, 1000], radius=20, fill=CARD_BG, outline=TEXT_CYAN, width=2)

    # Cabecera institucional
    d.text((960, 130), "CORPORACIÓN ESCUELA TECNOLÓGICA DEL ORIENTE", font=F_TITLE, fill=TEXT_WHITE, anchor="mm")
    d.text((960, 180), "FACULTAD DE INGENIERÍA · PROGRAMA DE INGENIERÍA DE SOFTWARE", font=F_SUBTITLE, fill=TEXT_MUTED, anchor="mm")
    d.text((960, 220), "ARQUITECTURA DE SOFTWARE — UNIDAD 2 · ACTIVIDAD 4", font=F_BODY_BOLD, fill=TEXT_AMBER, anchor="mm")

    d.line([300, 260, 1620, 260], fill=CARD_BORDER, width=2)

    # Título Principal
    d.text((960, 330), "TEJIENDO REDES: ARQUITECTURA ENTRE HILOS Y NODOS", font=F_HERO, fill=TEXT_CYAN, anchor="mm")
    d.text((960, 395), "NexusAI 2.0: De la Arquitectura Conceptual a la Red Física Distribuida", font=F_TITLE, fill=TEXT_WHITE, anchor="mm")
    d.text((960, 445), "Sustentación Técnica Formal y Demostración Operativa en Vivo del Clúster", font=F_SUBTITLE, fill=TEXT_MUTED, anchor="mm")

    # Tarjetas de Autores
    # Autor 1
    d.rounded_rectangle([250, 510, 920, 750], radius=14, fill=(30, 41, 59), outline=TEXT_CYAN, width=2)
    d.text((280, 545), "Juan Carlos Benítez Rojas", font=F_TITLE, fill=TEXT_WHITE)
    d.text((280, 595), "Líder de Proyecto y Arquitecto de Software", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((280, 645), "• Formalización arquitectónica en PlantUML (UML 2.5)", font=F_SMALL, fill=TEXT_MUTED)
    d.text((280, 680), "• Selección de patrones de diseño concurrentes", font=F_SMALL, fill=TEXT_MUTED)
    d.text((280, 715), "• Consolidación del informe formal bajo normas APA 7", font=F_SMALL, fill=TEXT_MUTED)

    # Autor 2
    d.rounded_rectangle([1000, 510, 1670, 750], radius=14, fill=(30, 41, 59), outline=TEXT_GREEN, width=2)
    d.text((1030, 545), "Juan José Córdoba Eraso", font=F_TITLE, fill=TEXT_WHITE)
    d.text((1030, 595), "Desarrollador Principal y Evaluador de Calidad", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((1030, 645), "• Implementación del clúster físico en Python 3.14", font=F_SMALL, fill=TEXT_MUTED)
    d.text((1030, 680), "• Automatización de suites de carga sintética y caos", font=F_SMALL, fill=TEXT_MUTED)
    d.text((1030, 715), "• Medición de contención, latencia p95 y balanceo", font=F_SMALL, fill=TEXT_MUTED)

    d.line([300, 790, 1620, 790], fill=CARD_BORDER, width=2)

    # Docente y Repositorio
    d.text((960, 835), "Docente Titular: Ing. Leidy Johana Polo", font=F_BODY_BOLD, fill=TEXT_WHITE, anchor="mm")
    d.text((960, 880), "Repositorio Oficial: https://github.com/Alboguaci/tejiendo-redes-nexusai", font=F_BODY, fill=TEXT_CYAN, anchor="mm")
    d.text((960, 930), "Bucaramanga, Colombia · Noviembre de 2026", font=F_SMALL, fill=TEXT_MUTED, anchor="mm")

    img.save(SLIDES_DIR / "intro.png")
    print("OK -> intro.png")

def generate_outro():
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([100, 80, 1820, 1000], radius=20, fill=CARD_BG, outline=TEXT_GREEN, width=2)

    d.text((960, 140), "NEXUSAI 2.0: PLATAFORMA DE MICROSERVICIOS COGNITIVOS", font=F_HERO, fill=TEXT_CYAN, anchor="mm")
    d.text((960, 200), "Conclusión de la Sustentación Oral y Demostración en Vivo", font=F_SUBTITLE, fill=TEXT_WHITE, anchor="mm")

    d.line([300, 245, 1620, 245], fill=CARD_BORDER, width=2)

    # 4 Cuadros de Logros
    cuadros = [
        ("MODELADO FORMAL UML", "3 Diagramas PlantUML", "Componentes (interfaces y puertos), Secuencia (concurrencia de hilos) y Despliegue en red.", TEXT_CYAN),
        ("PROTOTIPO ROBUSTO", "9 Módulos Python 3.14", "100% Biblioteca estándar. Sockets HTTP multi-hilo, pools acotados y broker con contrapresión.", TEXT_GREEN),
        ("9 PATRONES DE DISEÑO", "Saga, Breaker, Bulkhead...", "Orquestación resiliente, disyuntores de circuito, mamparos y balanceo Least-Connections.", TEXT_AMBER),
        ("RESULTADOS EMPÍRICOS", "1 200 Transacciones", "Speedup de 2,89× (96,5% de eficiencia), 100% disponibilidad ante fallos y 0 errores 500.", TEXT_CYAN)
    ]
    qx = 160
    qy = 280
    for i, (tit, sub, desc, col) in enumerate(cuadros):
        x = qx + (i % 2) * 820
        y = qy + (i // 2) * 230
        d.rounded_rectangle([x, y, x + 780, y + 200], radius=12, fill=(30, 41, 59), outline=col, width=1)
        d.text((x + 30, y + 25), tit, font=F_BODY_BOLD, fill=col)
        d.text((x + 30, y + 60), sub, font=F_SUBTITLE, fill=TEXT_WHITE)
        d.text((x + 30, y + 105), desc[:65], font=F_BODY, fill=TEXT_MUTED)
        if len(desc) > 65:
            d.text((x + 30, y + 140), desc[65:], font=F_BODY, fill=TEXT_MUTED)

    d.line([300, 775, 1620, 775], fill=CARD_BORDER, width=2)

    d.text((960, 820), "Repositorio: https://github.com/Alboguaci/tejiendo-redes-nexusai", font=F_TITLE, fill=TEXT_CYAN, anchor="mm")
    d.text((960, 875), "Informe Académico Oficial (20 Páginas APA 7) · Compendio de Anexos Técnicos (5 Páginas)", font=F_BODY, fill=TEXT_WHITE, anchor="mm")
    d.text((960, 920), "Agradecimientos a la Docente Leidy Johana Polo · Tecnológica del Oriente · 2026", font=F_SUBTITLE, fill=TEXT_AMBER, anchor="mm")

    img.save(SLIDES_DIR / "outro.png")
    print("OK -> outro.png")

if __name__ == "__main__":
    generate_intro()
    generate_outro()
