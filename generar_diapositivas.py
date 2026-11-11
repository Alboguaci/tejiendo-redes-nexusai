"""Generador de diapositivas en alta resolución (1920x1080) para el video de sustentación de NexusAI 2.0.

Crea 22 diapositivas temáticas para la presentación oral de la Actividad 4:
Tejiendo redes: Arquitectura de software entre hilos y nodos.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SLIDES_DIR = ROOT / "video_sustentacion" / "slides"
SLIDES_DIR.mkdir(parents=True, exist_ok=True)

# Tipografías del sistema
FONT_TITLE_PATH = r"C:\Windows\Fonts\segoeuib.ttf"   # Segoe UI Bold
FONT_REGULAR_PATH = r"C:\Windows\Fonts\segoeui.ttf"  # Segoe UI Regular
FONT_SEMI_PATH = r"C:\Windows\Fonts\segoeuisl.ttf"   # Segoe UI Semilight
FONT_MONO_PATH = r"C:\Windows\Fonts\consola.ttf"     # Consolas

def get_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

F_HEADER = get_font(FONT_TITLE_PATH, 22)
F_TITLE = get_font(FONT_TITLE_PATH, 32)
F_SUBTITLE = get_font(FONT_REGULAR_PATH, 20)
F_SECTION = get_font(FONT_TITLE_PATH, 16)
F_BODY = get_font(FONT_REGULAR_PATH, 19)
F_BODY_BOLD = get_font(FONT_TITLE_PATH, 19)
F_SMALL = get_font(FONT_REGULAR_PATH, 15)
F_MONO = get_font(FONT_MONO_PATH, 16)
F_BADGE = get_font(FONT_TITLE_PATH, 14)

# Paleta de colores Dark Tech
BG_COLOR = (11, 17, 32)          # #0B1120 (Slate 950)
HEADER_BG = (15, 23, 42)         # #0F172A (Slate 900)
CARD_BG = (30, 41, 59)           # #1E293B (Slate 800)
CARD_BORDER = (51, 65, 85)       # #334155 (Slate 700)
TEXT_WHITE = (248, 250, 252)     # #F8FAFC
TEXT_MUTED = (148, 163, 184)     # #94A3B8
TEXT_CYAN = (56, 189, 248)       # #38BDF8 (Sky 400)
TEXT_GREEN = (52, 211, 153)      # #34D399 (Emerald 400)
TEXT_AMBER = (251, 191, 36)      # #FBBF24 (Amber 400)
TEXT_RED = (248, 113, 113)       # #F87171 (Red 400)
LINE_COLOR = (30, 41, 59)

def draw_base_template(turno: int, speaker: str, speaker_name: str, speaker_role: str, section_name: str) -> Image.Image:
    img = Image.new("RGB", (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Barra superior (Header)
    draw.rectangle([0, 0, 1920, 80], fill=HEADER_BG)
    draw.line([0, 80, 1920, 80], fill=CARD_BORDER, width=2)

    # Texto Header
    draw.text((40, 18), "CORPORACIÓN ESCUELA TECNOLÓGICA DEL ORIENTE · FACULTAD DE INGENIERÍA", font=F_SMALL, fill=TEXT_MUTED)
    draw.text((40, 42), "ARQUITECTURA DE SOFTWARE — ACTIVIDAD 4: TEJIENDO REDES", font=F_HEADER, fill=TEXT_WHITE)

    # Badge Proyecto en Header
    badge_x = 1120
    draw.rounded_rectangle([badge_x, 20, badge_x + 220, 60], radius=8, fill=(12, 74, 110), outline=TEXT_CYAN, width=1)
    draw.text((badge_x + 22, 28), "NEXUSAI 2.0 CLUSTER", font=F_BADGE, fill=TEXT_WHITE)

    # 2. Contenedor de Contenido Principal (Izquierda)
    # x: 40..1340 (ancho 1300), y: 100..1010 (alto 910)
    draw.rounded_rectangle([40, 100, 1340, 1020], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)

    # 3. Contenedor del Expositor (Derecha)
    # x: 1360..1880 (ancho 520), y: 100..1020
    draw.rounded_rectangle([1360, 100, 1880, 1020], radius=16, fill=HEADER_BG, outline=CARD_BORDER, width=2)

    # Cabecera del panel del expositor
    accent_color = TEXT_CYAN if speaker == "JC" else TEXT_GREEN
    draw.rounded_rectangle([1375, 115, 1865, 160], radius=8, fill=CARD_BG, outline=accent_color, width=1)
    
    # Indicador Turno y Expositor
    draw.text((1390, 126), f"TURNO {turno:02d} / 22", font=F_BADGE, fill=accent_color)
    # Punto de directo
    draw.ellipse([1835, 132, 1847, 144], fill=(239, 68, 68))
    draw.text((1760, 126), "DIRECTO", font=F_SMALL, fill=TEXT_MUTED)

    # Área reservada para el video vertical (480x850 centrado)
    # x: 1380..1860 (ancho 480), y: 175..1005 (alto 830)
    draw.rounded_rectangle([1380, 175, 1860, 930], radius=12, fill=(0, 0, 0), outline=accent_color, width=2)

    # Pie del panel del expositor (Nombre y Rol)
    draw.rounded_rectangle([1375, 940, 1865, 1005], radius=8, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.text((1388, 948), speaker_name, font=F_BODY_BOLD, fill=TEXT_WHITE)
    draw.text((1388, 975), speaker_role, font=F_SMALL, fill=accent_color)

    # Barra inferior informativa dentro del área de contenido
    draw.text((60, 985), f"Sección: {section_name}", font=F_SMALL, fill=TEXT_MUTED)
    draw.text((1050, 985), "Repositorio: Alboguaci/tejiendo-redes-nexusai", font=F_SMALL, fill=TEXT_CYAN)

    return img

def add_header_titles(draw, category: str, title: str, subtitle: str = ""):
    draw.rounded_rectangle([60, 120, 60 + len(category)*11 + 20, 148], radius=6, fill=(15, 23, 42), outline=TEXT_CYAN, width=1)
    draw.text((70, 124), category.upper(), font=F_BADGE, fill=TEXT_CYAN)
    draw.text((60, 160), title, font=F_TITLE, fill=TEXT_WHITE)
    if subtitle:
        draw.text((60, 205), subtitle, font=F_SUBTITLE, fill=TEXT_MUTED)

def paste_fit_image(base_img: Image.Image, img_path: Path, box: tuple[int, int, int, int]):
    """Escala y pega una imagen dentro de la caja [x1, y1, x2, y2] manteniendo aspect ratio."""
    if not img_path.exists():
        return
    with Image.open(img_path) as im:
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        bx1, by1, bx2, by2 = box
        bw, bh = bx2 - bx1, by2 - by1
        iw, ih = im.size
        scale = min(bw / iw, bh / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        nx = bx1 + (bw - nw) // 2
        ny = by1 + (bh - nh) // 2
        base_img.paste(resized, (nx, ny), resized)

def generate_all_slides():
    print("Iniciando generación de 22 diapositivas...")
    
    # ----------------------------------------------------
    # TURNO 01: Portada y Presentación del Proyecto (JC)
    # ----------------------------------------------------
    img = draw_base_template(1, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Introducción y Portada")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Actividad 4 · Unidad 2", "Tejiendo Redes: Arquitectura entre Hilos y Nodos", "NexusAI 2.0: De la Arquitectura Conceptual a la Red Física")

    # Tarjeta de Contexto
    d.rounded_rectangle([60, 240, 1320, 480], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 265), "Propósito y Evolución Técnica:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 305), "• Evolución formal desde el diseño conceptual de microservicios de la Actividad 2.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 345), "• Construcción de un clúster físico real gobernado por contratos HTTP y sockets multi-hilo.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 385), "• Validación cuantitativa de escalabilidad horizontal y degradación controlada bajo caos.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 425), "• Medición objetiva de la interacción física entre hilos del gateway y nodos de cómputo.", font=F_BODY, fill=TEXT_WHITE)

    # Tarjetas de Integrantes
    d.rounded_rectangle([60, 510, 670, 720], radius=12, fill=HEADER_BG, outline=TEXT_CYAN, width=1)
    d.text((85, 535), "Juan Carlos Benítez Rojas", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((85, 570), "Líder de Proyecto & Arquitecto de Software", font=F_SUBTITLE, fill=TEXT_CYAN)
    d.text((85, 615), "• Formalización de modelos UML (PlantUML)", font=F_SMALL, fill=TEXT_MUTED)
    d.text((85, 645), "• Selección y fundamentación de patrones", font=F_SMALL, fill=TEXT_MUTED)
    d.text((85, 675), "• Consolidación del informe formal APA 7", font=F_SMALL, fill=TEXT_MUTED)

    d.rounded_rectangle([710, 510, 1320, 720], radius=12, fill=HEADER_BG, outline=TEXT_GREEN, width=1)
    d.text((735, 535), "Juan José Córdoba Eraso", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((735, 570), "Desarrollador Principal & Calidad", font=F_SUBTITLE, fill=TEXT_GREEN)
    d.text((735, 615), "• Implementación del clúster multi-hilo Python", font=F_SMALL, fill=TEXT_MUTED)
    d.text((735, 645), "• Automatización de suites de carga y caos", font=F_SMALL, fill=TEXT_MUTED)
    d.text((735, 675), "• Análisis de métricas, contención y balanceo", font=F_SMALL, fill=TEXT_MUTED)

    # Badges Inferiores
    badges = ["ISO/IEC 25010", "Python 3.14 Estándar", "9 Patrones de Diseño", "1 200 Transacciones", "0 Errores Críticos 500"]
    bx = 60
    for b in badges:
        bw = len(b) * 11 + 24
        d.rounded_rectangle([bx, 760, bx + bw, 805], radius=8, fill=(15, 23, 42), outline=CARD_BORDER, width=1)
        d.text((bx + 12, 772), b, font=F_BADGE, fill=TEXT_CYAN)
        bx += bw + 15
    img.save(SLIDES_DIR / "slide_01.png")

    # ----------------------------------------------------
    # TURNO 02: Dominio y Pipeline Cognitivo (JJ)
    # ----------------------------------------------------
    img = draw_base_template(2, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Dominio y Pipeline")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Dominio del Negocio", "Pipeline Cognitivo Distribuido en 3 Etapas", "Atención automatizada omnicanal con validación estricta de políticas y salvaguardas")

    # 3 Tarjetas del Pipeline
    etapas = [
        ("1. TRIAGE COGNITIVO", "Clasificación inicial de intención", "80 ms (±20 ms)", "I/O Bound",
         "Recepción y enrutamiento ágil de la solicitud omnicanal. Determina el perfil de riesgo y la categoría de consulta.", TEXT_CYAN),
        ("2. RAG CONTEXTUAL", "Recuperación semántica aumentada", "180 ms (±40 ms)", "Memory Bound",
         "Extracción de documentos y contexto vectorial relevante. Consulta bases documentales e inyecta contexto.", TEXT_GREEN),
        ("3. COMPLIANCE & ÉTICA", "Validación normativa y guardrails", "120 ms (±30 ms)", "CPU Bound",
         "Evaluación determinista de confianza semántica. Si cae bajo 0,90, rechaza y dispara la compensación Saga.", TEXT_AMBER)
    ]
    px = 60
    for titulo, subtitulo, lat, tipo, desc, col in etapas:
        d.rounded_rectangle([px, 260, px + 390, 740], radius=12, fill=HEADER_BG, outline=col, width=2)
        d.text((px + 25, 290), titulo, font=F_BODY_BOLD, fill=col)
        d.text((px + 25, 330), subtitulo, font=F_SMALL, fill=TEXT_WHITE)
        d.rounded_rectangle([px + 25, 370, px + 220, 405], radius=6, fill=CARD_BG)
        d.text((px + 35, 378), f"Latencia media: {lat}", font=F_BADGE, fill=TEXT_MUTED)
        d.rounded_rectangle([px + 25, 420, px + 180, 455], radius=6, fill=CARD_BG)
        d.text((px + 35, 428), f"Perfil: {tipo}", font=F_BADGE, fill=TEXT_CYAN)
        
        # Descripción
        lines = [desc[:42], desc[42:84], desc[84:]]
        ly = 480
        for l in lines:
            if l.strip():
                d.text((px + 25, ly), l.strip(), font=F_SMALL, fill=TEXT_MUTED)
                ly += 30
        px += 430

    d.rounded_rectangle([60, 780, 1320, 890], radius=10, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 805), "Clave Arquitectónica:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 845), "Se descartaron simulaciones cosméticas en frontend; el pipeline ejecuta procesos reales independientes en Python.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_02.png")

    # ----------------------------------------------------
    # TURNO 03: Diagrama de Componentes - Capa Superior (JC)
    # ----------------------------------------------------
    img = draw_base_template(3, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Modelado UML: Componentes")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Modelado Estructural UML", "Diagrama de Componentes: Capa de Coordinación", "API Gateway, Orquestador Saga, Balanceador de Carga y Circuit Breakers")
    paste_fit_image(img, ROOT / "diagramas" / "01_componentes.png", (60, 240, 700, 930))

    d.rounded_rectangle([730, 260, 1320, 880], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((760, 290), "Subsistema Coordinador (:8080):", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((760, 340), "• Punto de entrada REST único (POST /task).", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 390), "• Pool de despacho acotado a 16 hilos dedicados.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 440), "• Orquestador central de transacciones Saga.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 490), "• Circuit Breakers independientes por worker (w1..w3).", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 540), "• Balanceador de carga configurable (Round-Robin / Least-Conn).", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 590), "• Publicador asíncrono de eventos hacia el Broker (:8090).", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([760, 680, 1290, 840], radius=8, fill=CARD_BG, outline=TEXT_CYAN, width=1)
    d.text((780, 705), "Principio de Inversión de Dependencias:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((780, 745), "El gateway desconoce la implementación interna de los workers,", font=F_SMALL, fill=TEXT_WHITE)
    d.text((780, 775), "interactuando exclusivamente mediante contratos REST homogéneos.", font=F_SMALL, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_03.png")

    # ----------------------------------------------------
    # TURNO 04: Diagrama de Componentes - Capa Inferior (JJ)
    # ----------------------------------------------------
    img = draw_base_template(4, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Modelado UML: Workers y Broker")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Modelado Estructural UML", "Nodos Trabajadores de Cómputo y Event Broker", "Aislamiento por mamparos (Bulkhead) y auditoría inmutable en bitácora JSONL")
    paste_fit_image(img, ROOT / "diagramas" / "01_componentes.png", (60, 240, 700, 930))

    d.rounded_rectangle([730, 260, 1320, 880], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((760, 290), "Nodos Trabajadores (w1, w2, w3):", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((760, 340), "• Puertos físicos: :8101, :8102 y :8103.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 390), "• Servicios expuestos: Triage, RAG, Compliance.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 440), "• Pool privado Bulkhead acotado a 4 hilos por nodo.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 490), "• Nodos sin estado compartido (Stateless).", font=F_BODY, fill=TEXT_WHITE)

    d.text((760, 560), "Broker de Eventos (:8090):", font=F_BODY_BOLD, fill=TEXT_AMBER)
    d.text((760, 610), "• Cola interna thread-safe acotada con contrapresión.", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 660), "• Hilo dedicado de drenaje continuo a disco (events.jsonl).", font=F_BODY, fill=TEXT_WHITE)
    d.text((760, 710), "• Garantía: la auditoría jamás penaliza el pipeline.", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([760, 760, 1290, 840], radius=8, fill=CARD_BG, outline=TEXT_GREEN, width=1)
    d.text((780, 785), "Capacidad Paralela Nominal:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((780, 810), "3 nodos × 4 hilos = 12 slots de cómputo simultáneo sin contención.", font=F_SMALL, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_04.png")

    # ----------------------------------------------------
    # TURNO 05: Diagrama de Secuencia - Camino Feliz (JC)
    # ----------------------------------------------------
    img = draw_base_template(5, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Modelado UML: Secuencia")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Modelado Dinámico UML", "Diagrama de Secuencia: Sincronización de Hilos y Nodos", "Interacción temporal entre los hilos de despacho T1-T8 y los hilos de cómputo W1-W3")
    paste_fit_image(img, ROOT / "diagramas" / "02_secuencia.png", (60, 240, 1320, 700))

    d.rounded_rectangle([60, 730, 1320, 930], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 755), "Orquestación en Camino Feliz (Happy Path):", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 795), "1. Entrada POST /task -> Reserva de hilo en el pool de despacho del coordinador (T1..T8).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 835), "2. Emisión asíncrona saga.started al broker -> Invocación secuencial: w1 (Triage) -> w2 (RAG) -> w3 (Compliance).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 875), "3. Cada trabajador activa un hilo de su pool (W1..W3), liberándolo inmediatamente tras responder HTTP 200.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_05.png")

    # ----------------------------------------------------
    # TURNO 06: Diagrama de Secuencia - Compensación Saga (JJ)
    # ----------------------------------------------------
    img = draw_base_template(6, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Modelado UML: Compensación")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Modelado Dinámico UML", "Compensación Inversa de la Saga ante Fallo Normativo", "Reversión ordenada de transacciones cuando compliance detecta violación de guardrails")
    paste_fit_image(img, ROOT / "diagramas" / "02_secuencia.png", (60, 240, 1320, 700))

    d.rounded_rectangle([60, 730, 1320, 930], radius=12, fill=HEADER_BG, outline=TEXT_RED, width=1)
    d.text((90, 755), "Flujo de Compensación Inversa (Rollback):", font=F_BODY_BOLD, fill=TEXT_RED)
    d.text((90, 795), "• Rechazo en compliance: confianza semántica < 0,90 -> Error tipificado de negocio (reintento inútil).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 835), "• Orquestador Saga revierte en orden inverso: compensa RAG (libera contexto) y compensa Triage.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 875), "• Retorna al cliente HTTP 409 Conflict con trazabilidad total. Cero estados huérfanos o inconsistentes.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_06.png")

    # ----------------------------------------------------
    # TURNO 07: Diagrama de Despliegue en Red (JC)
    # ----------------------------------------------------
    img = draw_base_template(7, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Modelado UML: Despliegue")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Modelado Físico UML", "Diagrama de Despliegue: Procesos en Red Local y Docker", "Seis procesos de sistema operativo independientes comunicados sobre TCP/IP")
    paste_fit_image(img, ROOT / "diagramas" / "03_despliegue.png", (60, 240, 1320, 740))

    d.rounded_rectangle([60, 760, 1320, 930], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 785), "Mapeo Físico y Portabilidad Cloud-Native:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 825), "• 6 Procesos de SO: Cliente, Coordinador (:8080), Broker (:8090), 3 Workers (:8101..:8103) y Dashboard (:8088).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 865), "• Equivalencia directa con contenedores Docker: aislamiento por puertos sin modificar código.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_07.png")

    # ----------------------------------------------------
    # TURNO 08: Patrones de Diseño 1 - Saga y Broker (JJ)
    # ----------------------------------------------------
    img = draw_base_template(8, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Patrones: Saga y Broker")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Patrones de Diseño Arquitectónicos", "Saga Orquestada y Broker de Mensajería", "Fundamentación técnica respaldada en literatura canónica")

    # Tarjeta Saga
    d.rounded_rectangle([60, 260, 670, 760], radius=12, fill=HEADER_BG, outline=TEXT_CYAN, width=2)
    d.text((90, 290), "Saga Orquestada", font=F_TITLE, fill=TEXT_CYAN)
    d.text((90, 340), "Garcia-Molina & Salem (1987) / Richardson (2018)", font=F_SMALL, fill=TEXT_MUTED)
    d.text((90, 390), "Desafío:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((90, 420), "Consistencia transaccional sin bloqueos distribuidos (2PC).", font=F_BODY, fill=TEXT_MUTED)
    d.text((90, 470), "Solución e Implementación:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((90, 500), "• Máquina de estados en coordinator.py.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 540), "• Transacciones de compensación hacia atrás.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 580), "• Idempotencia en cada llamada de reversión.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 640), "Evidencia Empírica:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((90, 670), "31 de 31 transacciones compensadas con éxito (código 409).", font=F_BODY, fill=TEXT_GREEN)

    # Tarjeta Broker
    d.rounded_rectangle([710, 260, 1320, 760], radius=12, fill=HEADER_BG, outline=TEXT_AMBER, width=2)
    d.text((740, 290), "Message Broker", font=F_TITLE, fill=TEXT_AMBER)
    d.text((740, 340), "Hohpe & Woolf (2003) / Enterprise Integration Patterns", font=F_SMALL, fill=TEXT_MUTED)
    d.text((740, 390), "Desafío:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((740, 420), "Auditoría masiva sin degradar latencias del pipeline.", font=F_BODY, fill=TEXT_MUTED)
    d.text((740, 470), "Solución e Implementación:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((740, 500), "• Proceso broker.py independiente en puerto 8090.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 540), "• Cola thread-safe acotada con contrapresión.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 580), "• Drenaje asíncrono a archivo inmutable events.jsonl.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 640), "Evidencia Empírica:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((740, 670), "9 735 eventos auditados con cero pérdidas y cola residual en cero.", font=F_BODY, fill=TEXT_GREEN)
    img.save(SLIDES_DIR / "slide_08.png")

    # ----------------------------------------------------
    # TURNO 09: Patrones de Diseño 2 - Mediator, Gateway, Circuit Breaker (JC)
    # ----------------------------------------------------
    img = draw_base_template(9, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Patrones: Mediator, Gateway, Circuit Breaker")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Patrones de Diseño Arquitectónicos", "Mediator, API Gateway y Circuit Breaker", "Aislamiento de dependencias, fachada unificada y tolerancia a fallos")

    patrones_9 = [
        ("Mediator", "Gamma et al. (1994)", "Desacopla a los workers para que no se conozcan entre sí, evitando dependencias cruzadas O(n²).", TEXT_CYAN),
        ("API Gateway / Proxy", "Fowler (2014) / Newman (2021)", "Ofrece un punto de entrada único (POST /task), oculta la topología interna y traduce excepciones a códigos HTTP.", TEXT_GREEN),
        ("Circuit Breaker", "Nygard (2018) / Release It!", "Máquina de 3 estados: CLOSED (normal), OPEN (aislado tras 3 fallos por 5 s) y HALF-OPEN (prueba de recuperación).", TEXT_AMBER)
    ]
    py = 260
    for nom, ref, desc, col in patrones_9:
        d.rounded_rectangle([60, py, 1320, py + 180], radius=12, fill=HEADER_BG, outline=col, width=1)
        d.text((90, py + 25), nom, font=F_TITLE, fill=col)
        d.text((90, py + 70), ref, font=F_SMALL, fill=TEXT_MUTED)
        d.text((90, py + 110), desc, font=F_BODY, fill=TEXT_WHITE)
        py += 210
    img.save(SLIDES_DIR / "slide_09.png")

    # ----------------------------------------------------
    # TURNO 10: Patrones de Diseño 3 - Bulkhead, Observer, Strategy, Retry (JJ)
    # ----------------------------------------------------
    img = draw_base_template(10, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Patrones: Bulkhead, Observer, Strategy, Retry")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Patrones de Diseño Arquitectónicos", "Bulkhead, Observer Distribuido, Strategy y Retry", "Concurrencia aislada, telemetría reactiva y balanceo adaptativo")

    p10 = [
        ("Bulkhead (Mamparos)", "Aislamiento estanco de recursos: pool de 16 hilos en gateway y 4 por worker. La saturación de un nodo no ahoga al clúster."),
        ("Observer Distribuido", "Difusión asíncrona de eventos desde el broker hacia el dashboard. Actualización en tiempo real sin polling bloqueante."),
        ("Strategy (Balanceo)", "Encapsulación intercambiable de algoritmos de balanceo: Round-Robin vs Least-Connections tras una misma interfaz."),
        ("Retry Selectivo", "Reintentos con retroceso exponencial acotado exclusivamente ante fallas transitorias de red, suprimiendo reintentos en negocio.")
    ]
    py = 260
    for nom, desc in p10:
        d.rounded_rectangle([60, py, 1320, py + 145], radius=10, fill=HEADER_BG, outline=CARD_BORDER, width=1)
        d.text((90, py + 20), nom, font=F_BODY_BOLD, fill=TEXT_CYAN)
        d.text((90, py + 65), desc[:85], font=F_BODY, fill=TEXT_WHITE)
        if len(desc) > 85:
            d.text((90, py + 95), desc[85:], font=F_BODY, fill=TEXT_MUTED)
        py += 165
    img.save(SLIDES_DIR / "slide_10.png")

    # ----------------------------------------------------
    # TURNO 11: Implementación Modular del Clúster (JC)
    # ----------------------------------------------------
    img = draw_base_template(11, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Implementación: Módulos")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Implementación del Prototipo", "Estructura Modular del Clúster en Python 3.14", "Desarrollo basado exclusivamente en la biblioteca estándar (zero dependencies)")

    # Árbol de archivos
    d.rounded_rectangle([60, 260, 620, 890], radius=12, fill=HEADER_BG, outline=TEXT_CYAN, width=1)
    d.text((90, 290), "Árbol del Repositorio prototipo/:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    tree = [
        "prototipo/",
        "  ├── common.py        # DTOs, CircuitBreaker, logs",
        "  ├── coordinator.py   # Gateway, Saga, Balancer",
        "  ├── worker.py        # WorkerNode, cognitive steps",
        "  ├── broker.py        # EventBroker, backpressure",
        "  ├── cluster.py       # Orquestador de subprocesos",
        "  ├── run_cluster.py   # CLI de arranque del clúster",
        "  ├── dashboard.html   # Telemetría web en vivo",
        "pruebas/",
        "  ├── load_test.py     # Generador concurrente",
        "  ├── chaos_test.py    # Inyector de perturbaciones",
        "  └── benchmark.py     # Suite de 9 escenarios"
    ]
    ty = 340
    for t in tree:
        col = TEXT_CYAN if t.endswith("/") else TEXT_WHITE
        d.text((90, ty), t, font=F_MONO, fill=col)
        ty += 45

    # Justificación y ventajas
    d.rounded_rectangle([660, 260, 1320, 890], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((690, 290), "Decisiones de Ingeniería:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((690, 345), "• 100% Biblioteca Estándar:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((715, 385), "Uso nativo de http.server, socket, threading, queue, concurrent.futures y json.", font=F_SMALL, fill=TEXT_MUTED)
    d.text((715, 415), "Garantiza reproducibilidad absoluta en Linux, Windows y macOS sin pip install.", font=F_SMALL, fill=TEXT_MUTED)

    d.text((690, 480), "• Alta Cohesión y Bajo Acoplamiento:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((715, 520), "Cada módulo encapsula una responsabilidad arquitectónica única.", font=F_SMALL, fill=TEXT_MUTED)
    d.text((715, 550), "Permite reemplazar el broker en memoria por RabbitMQ o Kafka sin tocar workers.", font=F_SMALL, fill=TEXT_MUTED)

    d.text((690, 615), "• Contratos Fuertemente Tipificados:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((715, 655), "Esquemas JSON explícitos con validación estricta de campos y tipos de error.", font=F_SMALL, fill=TEXT_MUTED)
    img.save(SLIDES_DIR / "slide_11.png")

    # ----------------------------------------------------
    # TURNO 12: Concurrencia y Pools de Hilos (JJ)
    # ----------------------------------------------------
    img = draw_base_template(12, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Concurrencia: Hilos y Sockets")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Ingeniería de Concurrencia", "Jerarquía de Concurrencia en Cuatro Niveles", "Aislamiento de memoria virtual, pools acotados y sincronización de grano fino")

    niveles = [
        ("Nivel 1: Procesos Autónomos", "Cada nodo ejecuta en su propio intérprete Python con espacio de memoria aislado. Fallas en workers no afectan al coordinador ni al broker."),
        ("Nivel 2: Servidores HTTP Multi-Hilo", "ThreadingHTTPServer asigna un hilo efímero por cada socket TCP entrante, evitando bloqueos durante la transferencia de red."),
        ("Nivel 3: Pool de Despacho (Gateway)", "ThreadPoolExecutor acotado a 16 hilos. Actúa como barrera de entrada para admitir clientes concurrentes sin sobre-suscripción."),
        ("Nivel 4: Pool de Cómputo (Workers)", "Cada worker confina sus tareas en 4 hilos. 3 nodos × 4 hilos = 12 slots simultáneos con tiempo de CPU acotado y predecible.")
    ]
    py = 260
    for nom, desc in niveles:
        d.rounded_rectangle([60, py, 1320, py + 130], radius=10, fill=HEADER_BG, outline=TEXT_GREEN, width=1)
        d.text((90, py + 18), nom, font=F_BODY_BOLD, fill=TEXT_GREEN)
        d.text((90, py + 60), desc[:95], font=F_BODY, fill=TEXT_WHITE)
        if len(desc) > 95:
            d.text((90, py + 90), desc[95:], font=F_SMALL, fill=TEXT_MUTED)
        py += 155

    d.rounded_rectangle([60, 880, 1320, 940], radius=8, fill=CARD_BG, outline=TEXT_CYAN, width=1)
    d.text((90, 895), "Sincronización Interna:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((320, 895), "threading.Lock reentrantes de grano fino con retención < 10 microsegundos.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_12.png")

    # ----------------------------------------------------
    # TURNO 13: Demostración en Vivo: Arranque y Dashboard (JC)
    # ----------------------------------------------------
    img = draw_base_template(13, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Demostración: Arranque")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Demostración Operativa en Vivo", "Arranque del Clúster y Tablero de Observabilidad", "Inicialización coordinada de 6 subprocesos y verificación de salud en tiempo real")
    paste_fit_image(img, ROOT / "evidencias" / "dashboard.png", (60, 240, 780, 930))

    d.rounded_rectangle([810, 260, 1320, 880], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((840, 290), "Secuencia de Arranque:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((840, 340), "Comando ejecutado:", font=F_SMALL, fill=TEXT_MUTED)
    d.text((840, 370), "python run_cluster.py --workers 3", font=F_MONO, fill=TEXT_GREEN)
    
    d.text((840, 440), "Nodos Inicializados:", font=F_BODY_BOLD, fill=TEXT_WHITE)
    d.text((840, 480), "• Coordinador / Gateway en :8080 (OK)", font=F_SMALL, fill=TEXT_GREEN)
    d.text((840, 520), "• Broker de Eventos en :8090 (OK)", font=F_SMALL, fill=TEXT_GREEN)
    d.text((840, 560), "• Worker w1 en :8101 (OK)", font=F_SMALL, fill=TEXT_GREEN)
    d.text((840, 600), "• Worker w2 en :8102 (OK)", font=F_SMALL, fill=TEXT_GREEN)
    d.text((840, 640), "• Worker w3 en :8103 (OK)", font=F_SMALL, fill=TEXT_GREEN)
    d.text((840, 680), "• Dashboard Web en :8088 (OK)", font=F_SMALL, fill=TEXT_GREEN)

    d.text((840, 750), "Dashboard Web:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((840, 790), "Supervisa latencias, estado de circuitos,", font=F_SMALL, fill=TEXT_WHITE)
    d.text((840, 820), "rendimiento y eventos persistidos.", font=F_SMALL, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_13.png")

    # ----------------------------------------------------
    # TURNO 14: Carga Nominal (JJ)
    # ----------------------------------------------------
    img = draw_base_template(14, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Demostración: Carga Nominal")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Demostración Operativa en Vivo", "Inyección de Carga Nominal: 120 Transacciones", "Evaluación de rendimiento nominal con concurrencia de 24 hilos cliente")

    # Métricas clave
    metrics = [
        ("Throughput Efectivo", "26.37 rps", "Supera holgadamente la meta mínima de 20 rps.", TEXT_CYAN),
        ("Latencia p95", "1 033.6 ms", "Por debajo del límite máximo de 1 500 ms.", TEXT_GREEN),
        ("Tasa de Éxito", "100.0 %", "120 tareas atendidas con cero errores de sistema 500.", TEXT_AMBER),
        ("Auditoría Broker", "100.0 %", "Eventos publicados = consumidos (cola residual en 0).", TEXT_GREEN)
    ]
    mx = 60
    my = 260
    for i, (tit, val, sub, col) in enumerate(metrics):
        x = mx + (i % 2) * 630
        y = my + (i // 2) * 220
        d.rounded_rectangle([x, y, x + 600, y + 190], radius=12, fill=HEADER_BG, outline=col, width=2)
        d.text((x + 30, y + 25), tit, font=F_SUBTITLE, fill=TEXT_MUTED)
        d.text((x + 30, y + 65), val, font=F_TITLE, fill=col)
        d.text((x + 30, y + 130), sub, font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([60, 740, 1320, 890], radius=10, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 765), "Comando Ejecutado:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 805), "python load_test.py --tasks 120 --concurrency 24 --label demo_nominal", font=F_MONO, fill=TEXT_GREEN)
    d.text((90, 845), "Demuestra que bajo condiciones normales el clúster satura eficientemente los 12 slots de cómputo.", font=F_SMALL, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_14.png")

    # ----------------------------------------------------
    # TURNO 15: Caos 1 - Inyección de Latencia (JC)
    # ----------------------------------------------------
    img = draw_base_template(15, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Caos: Inyección de Latencia")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Suite de Caos Controlado", "Escenario 1: Inyección de Latencia (+300 ms en w2)", "Demostración del efecto de nodos lentos bajo balanceo Round-Robin")

    d.rounded_rectangle([60, 260, 1320, 520], radius=12, fill=HEADER_BG, outline=TEXT_AMBER, width=2)
    d.text((90, 290), "Condición Experimental Inyectada:", font=F_BODY_BOLD, fill=TEXT_AMBER)
    d.text((90, 335), "python chaos_test.py latency --worker http://127.0.0.1:8102 --ms 300", font=F_MONO, fill=TEXT_WHITE)
    d.text((90, 395), "• Se induce un retardo artificial de 300 milisegundos en el trabajador w2.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 435), "• El nodo sigue respondiendo OK, pero acumula tiempo de ocupación en sus hilos.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 475), "• El orquestador ejecuta la carga con estrategia Round-Robin ciega a la carga.", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([60, 550, 1320, 890], radius=12, fill=HEADER_BG, outline=TEXT_RED, width=1)
    d.text((90, 580), "Efecto Observado en el Clúster:", font=F_BODY_BOLD, fill=TEXT_RED)
    d.text((90, 625), "• Throughput cae de 26,37 rps a 8,83 rps (-66,5 % de capacidad).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 665), "• Latencia p95 se dispara de 1 033 ms a 4 128 ms.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 715), "Hallazgo Arquitectónico:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 755), "El mamparo (Bulkhead) por trabajador no protege al coordinador si el algoritmo de balanceo", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 795), "continúa enviando el 33% del tráfico al nodo retrasado, saturando los hilos de despacho.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_15.png")

    # ----------------------------------------------------
    # TURNO 16: Caos 2 - Fallo 100% y Circuit Breaker (JJ)
    # ----------------------------------------------------
    img = draw_base_template(16, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Caos: Fallo 100% y Circuit Breaker")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Suite de Caos Controlado", "Escenario 2: Fallo Total en w2 y Aislamiento por Circuit Breaker", "Activación del disyuntor tras 3 fallos consecutivos y redirección transparente de tráfico")

    d.rounded_rectangle([60, 260, 1320, 540], radius=12, fill=HEADER_BG, outline=TEXT_RED, width=2)
    d.text((90, 290), "Transición de Estados del Circuit Breaker:", font=F_BODY_BOLD, fill=TEXT_RED)
    d.text((90, 335), "1. Estado Inicial: CLOSED (operación nominal en los tres nodos).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 380), "2. Inyección: python chaos_test.py fail --worker :8102 --rate 1.0 (100% fallos en w2).", font=F_MONO, fill=TEXT_AMBER)
    d.text((90, 430), "3. Conmuta a OPEN: tras 3 excepciones sucesivas, w2 queda aislado durante 5 segundos.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 475), "4. Redirección: el coordinador desvía automáticamente las peticiones hacia w1 y w3.", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([60, 570, 1320, 890], radius=12, fill=HEADER_BG, outline=TEXT_GREEN, width=1)
    d.text((90, 600), "Resultado Cuantitativo Categórico:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((90, 645), "• 120 / 120 transacciones atendidas exitosamente (100 % disponibilidad).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 685), "• Throughput sostenido: 17,87 rps (dos trabajadores sanos absorben el 100% de la demanda).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 725), "• Cero errores 500 entregados al cliente final.", font=F_BODY, fill=TEXT_GREEN)
    d.text((90, 775), "Conclusión: El disyuntor previene la degradación en cascada y mantiene vivo el sistema.", font=F_BODY_BOLD, fill=TEXT_CYAN)
    img.save(SLIDES_DIR / "slide_16.png")

    # ----------------------------------------------------
    # TURNO 17: Caos 3 - Guardrails y Reversión Saga (JC)
    # ----------------------------------------------------
    img = draw_base_template(17, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Caos: Guardrails y Saga")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Suite de Caos Controlado", "Escenario 3: Rechazo Normativo en Compliance (25%)", "Ejecución de compensaciones inversas para garantizar consistencia eventual")

    d.rounded_rectangle([60, 260, 670, 700], radius=12, fill=HEADER_BG, outline=TEXT_AMBER, width=2)
    d.text((90, 290), "Inyección de Reglas de Negocio:", font=F_BODY_BOLD, fill=TEXT_AMBER)
    d.text((90, 335), "python chaos_test.py guardrail --tasks 120 --rate 0.25", font=F_MONO, fill=TEXT_WHITE)
    d.text((90, 395), "• 25 % de las peticiones violan políticas éticas.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 440), "• Triage completa OK (w1).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 485), "• RAG completa OK (w2).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 530), "• Compliance rechaza en etapa 3 (w3).", font=F_BODY, fill=TEXT_RED)
    d.text((90, 585), "Mecanismo:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 625), "El orquestador dispara compensación inversa:", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 660), "1° revierte RAG -> 2° revierte Triage.", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([710, 260, 1320, 700], radius=12, fill=HEADER_BG, outline=TEXT_GREEN, width=2)
    d.text((740, 290), "Balance de Ejecución:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((740, 345), "• 89 Transacciones completadas (HTTP 200).", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 395), "• 31 Transacciones rechazadas y compensadas (HTTP 409).", font=F_BODY, fill=TEXT_AMBER)
    d.text((740, 445), "• 0 Transacciones con estado huérfano o inconsistente.", font=F_BODY, fill=TEXT_GREEN)
    d.text((740, 495), "• 100 % de transacciones gestionadas con éxito.", font=F_BODY, fill=TEXT_GREEN)
    d.text((740, 560), "Velocidad de Reversión:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((740, 600), "La compensación total se ejecuta en < 100 ms por transacción.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 645), "Throughput sostenido de la prueba: 23,82 rps.", font=F_BODY, fill=TEXT_WHITE)

    d.rounded_rectangle([60, 730, 1320, 890], radius=10, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 765), "Principio Clave:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 805), "Una compensación ordenada no es un error de sistema; es una respuesta de negocio válida con código 409.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_17.png")

    # ----------------------------------------------------
    # TURNO 18: Caos 4 - Caída Física y Recuperación (JJ)
    # ----------------------------------------------------
    img = draw_base_template(18, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Caos: Caída Física y Recuperación")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Suite de Caos Controlado", "Escenario 4: Caída de Proceso w3 y Reinserción en Caliente", "Prueba de recuperación elástica mediante estado HALF-OPEN del Circuit Breaker")

    d.rounded_rectangle([60, 260, 670, 720], radius=12, fill=HEADER_BG, outline=TEXT_RED, width=1)
    d.text((90, 290), "Fase 1: Terminación Física de Nodo", font=F_BODY_BOLD, fill=TEXT_RED)
    d.text((90, 335), "python chaos_test.py stop --worker :8103", font=F_MONO, fill=TEXT_WHITE)
    d.text((90, 390), "• Se mata físicamente el proceso del trabajador w3.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 435), "• Gateway detecta ConnectionRefusedError.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 480), "• Circuit Breaker de w3 conmuta a OPEN.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 525), "• w1 y w2 absorben la carga sin interrupción.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 580), "Throughput obtenido: 14,55 rps (100% atendidas).", font=F_BODY_BOLD, fill=TEXT_AMBER)

    d.rounded_rectangle([710, 260, 1320, 720], radius=12, fill=HEADER_BG, outline=TEXT_GREEN, width=1)
    d.text((740, 290), "Fase 2: Reinicio en Caliente", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((740, 335), "python worker.py --port 8103 (en terminal 3)", font=F_MONO, fill=TEXT_WHITE)
    d.text((740, 390), "• El proceso w3 vuelve a levantar su socket.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 435), "• Expira el periodo de enfriamiento (5 segundos).", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 480), "• Breaker entra en HALF-OPEN y envía prueba.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 525), "• Respuesta exitosa -> Conmuta a CLOSED.", font=F_BODY, fill=TEXT_WHITE)
    d.text((740, 580), "Throughput restituido: 23,53 rps (p95: 518 ms).", font=F_BODY_BOLD, fill=TEXT_GREEN)

    d.rounded_rectangle([60, 750, 1320, 890], radius=10, fill=HEADER_BG, outline=TEXT_CYAN, width=1)
    d.text((90, 780), "Elasticidad Confirmada:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 820), "El clúster integra y desintegra nodos de cómputo en caliente sin reiniciar el coordinador.", font=F_BODY, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_18.png")

    # ----------------------------------------------------
    # TURNO 19: Resultados de Escalabilidad y Latencia (JC)
    # ----------------------------------------------------
    img = draw_base_template(19, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Resultados: Escalabilidad")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Evaluación Experimental Cuantitativa", "Escalabilidad Horizontal y Abatimiento de Latencia", "Curvas de rendimiento empírico sobre 180 transacciones con 24 clientes concurrentes")

    paste_fit_image(img, ROOT / "pruebas" / "graficas" / "01_escalabilidad_throughput.png", (60, 250, 680, 680))
    paste_fit_image(img, ROOT / "pruebas" / "graficas" / "02_escalabilidad_latencia.png", (700, 250, 1320, 680))

    # Tabla resumen inferior
    d.rounded_rectangle([60, 700, 1320, 930], radius=12, fill=HEADER_BG, outline=TEXT_CYAN, width=1)
    d.text((90, 725), "Métricas Clave de Escalabilidad:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 765), "• 1 Nodo:   Throughput =  9,24 rps  |  Speedup = 1,00×  |  Eficiencia = 100,0 %  |  Latencia p95 = 3 185 ms", font=F_MONO, fill=TEXT_WHITE)
    d.text((90, 805), "• 2 Nodos:  Throughput = 18,14 rps  |  Speedup = 1,96×  |  Eficiencia =  98,2 %  |  Latencia p95 = 1 617 ms", font=F_MONO, fill=TEXT_WHITE)
    d.text((90, 845), "• 3 Nodos:  Throughput = 26,74 rps  |  Speedup = 2,89×  |  Eficiencia =  96,5 %  |  Latencia p95 = 1 043 ms", font=F_MONO, fill=TEXT_GREEN)
    d.text((90, 890), "Conclusión: Escalado casi lineal (96,5% de eficiencia) y reducción de latencia a un tercio por descongestión de colas.", font=F_SMALL, fill=TEXT_CYAN)
    img.save(SLIDES_DIR / "slide_19.png")

    # ----------------------------------------------------
    # TURNO 20: Optimización: Least-Connections vs Round-Robin (JJ)
    # ----------------------------------------------------
    img = draw_base_template(20, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Ajustes: Balanceo Adaptativo")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Optimizaciones Derivadas de la Medición", "Balanceo Adaptativo: Least-Connections vs Round-Robin", "Mitigación del impacto de nodos lentos y resolución de nombres en 127.0.0.1")

    paste_fit_image(img, ROOT / "pruebas" / "graficas" / "05_estrategias.png", (60, 250, 750, 720))

    d.rounded_rectangle([780, 250, 1320, 720], radius=12, fill=HEADER_BG, outline=TEXT_GREEN, width=2)
    d.text((810, 280), "Comparativa bajo Nodo Lento (+300 ms):", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((810, 335), "1. Round-Robin (Ciego a la carga):", font=F_BODY_BOLD, fill=TEXT_RED)
    d.text((810, 370), "• Throughput: 8,99 rps", font=F_BODY, fill=TEXT_WHITE)
    d.text((810, 405), "• Latencia p95: 4 128,4 ms", font=F_BODY, fill=TEXT_WHITE)
    d.text((810, 440), "• Retención de capacidad: solo 34,5 %", font=F_BODY, fill=TEXT_WHITE)

    d.text((810, 500), "2. Least-Connections (Consciente):", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((810, 535), "• Throughput: 20,59 rps (+129 % de caudal)", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((810, 575), "• Latencia p95: 1 548,2 ms (-62,5 % latencia)", font=F_BODY, fill=TEXT_WHITE)
    d.text((810, 615), "• Retención de capacidad: 75,7 %", font=F_BODY, fill=TEXT_WHITE)
    d.text((810, 660), "Desvía tráfico hacia nodos con menor cola activa.", font=F_SMALL, fill=TEXT_CYAN)

    # Ajuste localhost
    d.rounded_rectangle([60, 750, 1320, 930], radius=10, fill=HEADER_BG, outline=TEXT_AMBER, width=1)
    d.text((90, 775), "Ajuste Crucial: La Trampa de 'localhost' en Windows", font=F_BODY_BOLD, fill=TEXT_AMBER)
    d.text((90, 815), "• La resolución de 'localhost' forzaba un sondeo IPv6 fallido antes de pasar a IPv4, añadiendo 2 042 ms por petición.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 855), "• Vincular estrictamente a '127.0.0.1' redujo la latencia por llamada a 2,15 ms (factor de aceleración de 951,5×).", font=F_BODY_BOLD, fill=TEXT_GREEN)
    img.save(SLIDES_DIR / "slide_20.png")

    # ----------------------------------------------------
    # TURNO 21: Balance de Metas Cumplidas (JC)
    # ----------------------------------------------------
    img = draw_base_template(21, "JC", "Juan Carlos Benítez Rojas", "Líder de Proyecto y Arquitecto", "Balance de Metas y Conclusiones")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Evaluación de Calidad ISO/IEC 25010", "Balance Consolidado de Metas del Sistema", "100% de objetivos arquitectónicos superados con evidencia experimental")

    metas = [
        ("Escalabilidad con 3 nodos", "Throughput >= 2.5x base; Eficiencia >= 80 %", "Speedup: 2.89x; Eficiencia: 96.5 %", "SUPERADA", TEXT_GREEN),
        ("Robustez ante nodo caído", "100% transacciones atendidas sin errores 500", "100% atendidas; 0 errores en 1 200 pruebas", "CUMPLIDA", TEXT_GREEN),
        ("Latencia extremo a extremo", "Percentil 95 (p95) < 1 500 ms con tres nodos", "p95 obtenido: 1 043,4 ms en línea base", "SUPERADA", TEXT_GREEN),
        ("Resiliencia transaccional", "100% compensación en rechazos de guardrail", "31 de 31 transacciones compensadas (409)", "CUMPLIDA", TEXT_GREEN),
        ("Trazabilidad de auditoría", "Registro íntegro sin descarte en colas", "9 735 eventos publicados = 9 735 consumidos", "CUMPLIDA", TEXT_GREEN)
    ]
    py = 250
    for met, obj, res, est, col in metas:
        d.rounded_rectangle([60, py, 1320, py + 105], radius=8, fill=HEADER_BG, outline=CARD_BORDER, width=1)
        d.text((85, py + 15), met, font=F_BODY_BOLD, fill=TEXT_WHITE)
        d.text((85, py + 55), f"Objetivo: {obj}", font=F_SMALL, fill=TEXT_MUTED)
        d.text((700, py + 55), f"Resultado: {res}", font=F_SMALL, fill=TEXT_CYAN)
        
        # Badge Estado
        d.rounded_rectangle([1150, py + 25, 1290, py + 75], radius=6, fill=(6, 78, 59), outline=col, width=1)
        d.text((1170, py + 38), est, font=F_BADGE, fill=col)
        py += 120

    d.rounded_rectangle([60, 860, 1320, 935], radius=8, fill=CARD_BG, outline=TEXT_CYAN, width=1)
    d.text((90, 875), "Conclusión Arquitectónica:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 902), "La concurrencia física, las colas y la propagación de fallas son propiedades emergentes que requieren validación en red.", font=F_SMALL, fill=TEXT_WHITE)
    img.save(SLIDES_DIR / "slide_21.png")

    # ----------------------------------------------------
    # TURNO 22: Repositorio Oficial y Despedida (JJ)
    # ----------------------------------------------------
    img = draw_base_template(22, "JJ", "Juan José Córdoba Eraso", "Desarrollador y Evaluador", "Entregables y Cierre")
    d = ImageDraw.Draw(img)
    add_header_titles(d, "Entregables Oficiales", "Repositorio Central de Código y Documentación", "NexusAI 2.0: Plataforma Cloud-Native de Microservicios Cognitivos")

    # Card Repositorio
    d.rounded_rectangle([60, 260, 1320, 480], radius=12, fill=HEADER_BG, outline=TEXT_CYAN, width=2)
    d.text((90, 290), "Repositorio Oficial en GitHub:", font=F_BODY_BOLD, fill=TEXT_CYAN)
    d.text((90, 335), "https://github.com/Alboguaci/tejiendo-redes-nexusai", font=F_TITLE, fill=TEXT_WHITE)
    d.text((90, 395), "• Código fuente completo del clúster (coordinador, workers, broker, dashboard).", font=F_BODY, fill=TEXT_MUTED)
    d.text((90, 435), "• Suites reproducibles de prueba de carga, inyección de caos y generación de gráficas.", font=F_BODY, fill=TEXT_MUTED)

    # Card Entregables Académicos
    d.rounded_rectangle([60, 510, 1320, 750], radius=12, fill=HEADER_BG, outline=CARD_BORDER, width=1)
    d.text((90, 535), "Entregables Documentales y Multimedia:", font=F_BODY_BOLD, fill=TEXT_GREEN)
    d.text((90, 575), "1. Informe Técnico Académico bajo Normas APA 7ma Edición (20 páginas consolidadas).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 615), "2. Compendio de Anexos Técnicos y Evidencias de Ejecución (5 páginas con logs, contratos y tablas).", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 655), "3. Modelos PlantUML versionados: componentes, secuencia con hilos y despliegue físico.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 695), "4. Video de Sustentación Oral y Demostración en Vivo (16 minutos, YouTube modo No listado).", font=F_BODY, fill=TEXT_WHITE)

    # Agradecimientos
    d.rounded_rectangle([60, 780, 1320, 930], radius=10, fill=(15, 23, 42), outline=TEXT_AMBER, width=1)
    d.text((90, 805), "Agradecimientos Académicos:", font=F_BODY_BOLD, fill=TEXT_AMBER)
    d.text((90, 845), "A la profesora Leidy Johana Polo por su valiosa orientación y rigor conceptual a lo largo del curso.", font=F_BODY, fill=TEXT_WHITE)
    d.text((90, 885), "Corporación Escuela Tecnológica del Oriente · Ingeniería de Software · Noviembre 2026", font=F_SMALL, fill=TEXT_MUTED)
    img.save(SLIDES_DIR / "slide_22.png")

    print("¡Las 22 diapositivas se generaron exitosamente en video_sustentacion/slides/!")

if __name__ == "__main__":
    generate_all_slides()
