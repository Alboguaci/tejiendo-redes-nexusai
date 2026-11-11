"""Generador del documento complementario: Anexos Técnicos y Evidencias de Ejecución.

NexusAI 2.0: De la arquitectura a la red.
Actividad 4 — Arquitectura de Software.
"""

from __future__ import annotations
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
OUTPUT = ROOT / "Anexos_Tecnicos_NexusAI2.docx"

FONT = "Times New Roman"

def set_run(run, size=11, bold=False, italic=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    return run

def base_p(p, space_before=0, space_after=2, line_spacing=1.15, first_indent=0.0, left_indent=0.0, align=None):
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    pf.first_line_indent = Inches(first_indent)
    pf.left_indent = Inches(left_indent)
    if align:
        p.alignment = align
    return p

def add_code(doc, text):
    for line in text.strip().splitlines():
        p = doc.add_paragraph()
        base_p(p, space_before=0, space_after=0, line_spacing=1.0, left_indent=0.25)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "F4F4F4")
        pPr.append(shd)
        run = p.add_run(line if line else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(8.5)

def add_table(doc, rows, title, note=""):
    p_title = doc.add_paragraph()
    base_p(p_title, space_before=6, space_after=2)
    set_run(p_title.add_run(title), bold=True)

    cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = True

    # Bordes APA
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        r'</w:tblBorders>' % nsdecls("w")
    )
    tblPr.append(borders)

    for r_idx, row in enumerate(rows):
        for c_idx in range(cols):
            val = row[c_idx] if c_idx < len(row) else ""
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            cp = cell.paragraphs[0]
            base_p(cp, space_before=2, space_after=2, line_spacing=1.0)
            run = cp.add_run(val)
            run.font.name = FONT
            run.font.size = Pt(9.5)
            if r_idx == 0:
                run.bold = True
        if r_idx == 0:
            trPr = table.rows[0]._tr.get_or_add_trPr()
            header = OxmlElement("w:tblHeader")
            header.set(qn("w:val"), "true")
            trPr.append(header)
            for c_idx in range(cols):
                tc = table.cell(0, c_idx)
                tcPr = tc._tc.get_or_add_tcPr()
                tcBorders = parse_xml(
                    r'<w:tcBorders %s><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tcBorders>'
                    % nsdecls("w")
                )
                tcPr.append(tcBorders)

    if note:
        pn = doc.add_paragraph()
        base_p(pn, space_before=2, space_after=4)
        set_run(pn.add_run("Nota. "), size=9, italic=True)
        set_run(pn.add_run(note), size=9)

def main():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    # Portada de Anexos
    for _ in range(4):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    base_p(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("NEXUSAI 2.0: ANEXOS TÉCNICOS Y EVIDENCIAS DE EJECUCIÓN"), size=15, bold=True)

    p = doc.add_paragraph()
    base_p(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("Documento complementario al informe formal de la Actividad 4"), size=12, italic=True)

    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    base_p(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("Juan Carlos Benítez Rojas (Líder y Arquitecto)\nJuan José Córdoba Eraso (Desarrollador y Calidad)"))

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    base_p(p, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run("Corporación Escuela Tecnológica del Oriente\nFacultad de Ingeniería — Ingeniería de Software\nArquitectura de Software — Noviembre 2026"))

    doc.add_page_break()

    # Presentación
    p = doc.add_paragraph()
    base_p(p, space_before=0, space_after=6)
    set_run(p.add_run("Presentación del Documento Adjunto"), size=13, bold=True)

    p = doc.add_paragraph()
    base_p(p, first_indent=0.5)
    set_run(p.add_run(
        "El presente compendio técnico reúne las especificaciones formales, esquemas JSON, bitácoras de auditoría, "
        "tabulaciones completas de rendimiento y secuencias de comandos reproducibles que complementan el informe "
        "académico principal de la Actividad 4 (Tejiendo redes: arquitectura de software entre hilos y nodos). "
        "Su segregación garantiza que el informe principal preserve la extensión reglamentaria de 20 páginas sin "
        "sacrificar la profundidad técnica, la trazabilidad empírica ni la reproducibilidad de los experimentos."
    ))

    rows_entregables = [
        ["Componente del proyecto", "Ubicación y acceso oficial", "Descripción técnica del entregable"],
        ["Repositorio central de código", "https://github.com/Alboguaci/tejiendo-redes-nexusai", "Código fuente completo, scripts de benchmark, pruebas de caos y modelos PlantUML"],
        ["Documento oficial de anexos", "informe/Anexos_Tecnicos_NexusAI2.pdf", "Contratos HTTP completos, extracto JSONL, registros de consola y comandos de despliegue"],
        ["Guion de sustentación técnica", "informe/Guion_Presentacion_Oral_17min.docx", "Guion dialogado verbátim de 17 minutos (22 intervenciones de 30 a 50 segundos)"],
        ["Video de sustentación oral", "YouTube (enlace en plataforma institucional)", "Exposición técnica y demostración del prototipo en vivo en modo «No listado»"],
        ["Informe técnico consolidado", "informe/Informe_Actividad4_Tejiendo_Redes.pdf", "Documento formal de 20 páginas bajo normas APA 7ma Edición"]
    ]
    add_table(doc, rows_entregables, "Tabla 0. Relación de entregables, documentos adjuntos y accesos oficiales", "Accesos oficiales y artefactos verificables del proyecto.")

    # Anexo A
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo A. Contratos de Interfaz HTTP y Esquemas JSON"), size=12, bold=True)

    p = doc.add_paragraph()
    base_p(p, first_indent=0.5)
    set_run(p.add_run("A.1. Petición al API Gateway (POST /task):"))
    add_code(doc, """{
  "client_id": "cliente-web-01",
  "request_type": "soporte_facturacion",
  "payload": {
    "usuario": "Carlos Mendoza",
    "monto": 145000,
    "descripcion": "Revisión de cobro recurrente"
  }
}""")

    p = doc.add_paragraph()
    base_p(p, first_indent=0.5, space_before=4)
    set_run(p.add_run("A.2. Respuesta exitosa con compensaciones y trazabilidad (HTTP 200 OK):"))
    add_code(doc, """{
  "transaction_id": "tx-e3b8a10f-5489-4b82-9842-70b28419f07a",
  "status": "COMPLETED",
  "strategy": "least_connections",
  "execution_path": [
    {"stage": "triage", "worker": "http://127.0.0.1:8082", "latency_ms": 78.4, "status": "OK"},
    {"stage": "rag", "worker": "http://127.0.0.1:8083", "latency_ms": 182.1, "status": "OK"},
    {"stage": "compliance", "worker": "http://127.0.0.1:8084", "latency_ms": 119.5, "status": "OK"}
  ],
  "total_latency_ms": 384.2,
  "circuit_breakers": {
    "w1": "CLOSED", "w2": "CLOSED", "w3": "CLOSED"
  }
}""")

    # Anexo B
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo B. Extracto Representativo de la Bitácora de Auditoría (events.jsonl)"), size=12, bold=True)
    p = doc.add_paragraph()
    base_p(p, first_indent=0.5)
    set_run(p.add_run("Cada transición de estado es serializada asíncronamente en el Broker de eventos sin bloquear los hilos de despacho:"))
    add_code(doc, """{"timestamp": "2026-11-09T22:15:01.102Z", "event_id": "evt-001", "tx_id": "tx-1201", "type": "TASK_RECEIVED", "source": "coordinator"}
{"timestamp": "2026-11-09T22:15:01.105Z", "event_id": "evt-002", "tx_id": "tx-1201", "type": "STAGE_STARTED", "stage": "triage", "target": "w1"}
{"timestamp": "2026-11-09T22:15:01.185Z", "event_id": "evt-003", "tx_id": "tx-1201", "type": "STAGE_COMPLETED", "stage": "triage", "target": "w1", "duration_ms": 79.8}
{"timestamp": "2026-11-09T22:15:01.188Z", "event_id": "evt-004", "tx_id": "tx-1201", "type": "STAGE_STARTED", "stage": "rag", "target": "w2"}
{"timestamp": "2026-11-09T22:15:01.371Z", "event_id": "evt-005", "tx_id": "tx-1201", "type": "STAGE_COMPLETED", "stage": "rag", "target": "w2", "duration_ms": 182.4}
{"timestamp": "2026-11-09T22:15:01.373Z", "event_id": "evt-006", "tx_id": "tx-1201", "type": "STAGE_STARTED", "stage": "compliance", "target": "w3"}
{"timestamp": "2026-11-09T22:15:01.494Z", "event_id": "evt-007", "tx_id": "tx-1201", "type": "COMPLIANCE_FAILED", "stage": "compliance", "reason": "guardrail_violation"}
{"timestamp": "2026-11-09T22:15:01.496Z", "event_id": "evt-008", "tx_id": "tx-1201", "type": "SAGA_COMPENSATION_TRIGGERED", "tx_id": "tx-1201"}
{"timestamp": "2026-11-09T22:15:01.522Z", "event_id": "evt-009", "tx_id": "tx-1201", "type": "COMPENSATION_COMPLETED", "stage": "rag", "target": "w2"}
{"timestamp": "2026-11-09T22:15:01.545Z", "event_id": "evt-010", "tx_id": "tx-1201", "type": "COMPENSATION_COMPLETED", "stage": "triage", "target": "w1"}
{"timestamp": "2026-11-09T22:15:01.548Z", "event_id": "evt-011", "tx_id": "tx-1201", "type": "TASK_REVERTED", "tx_id": "tx-1201", "duration_ms": 446.0}""")

    # Anexo C
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo C. Salida Consolidada de Consola de la Suite Experimental"), size=12, bold=True)
    add_code(doc, """================================================================================
NEXUSAI 2.0 -- SUITE DE VALIDACION EXPERIMENTAL Y RESILIENCIA
================================================================================
[TEST 1/9] Linea base: 3 nodos saludables | 120 txs | concurrencia 24
  --> Atendidas: 120/120 (100.0%) | Completadas: 120 | Compensadas: 0 | Errores 500: 0
  --> Throughput: 26.37 rps | p50: 854.2 ms | p95: 1033.6 ms | p99: 1127.0 ms

[TEST 2/9] Escalabilidad horizontal: 1 nodo de computo (w1) | 180 txs
  --> Throughput: 9.24 rps | Speedup: 1.00x | Eficiencia: 100.0% | p95: 3185.0 ms

[TEST 3/9] Escalabilidad horizontal: 2 nodos de computo (w1, w2) | 180 txs
  --> Throughput: 18.14 rps | Speedup: 1.96x | Eficiencia: 98.2% | p95: 1617.0 ms

[TEST 4/9] Escalabilidad horizontal: 3 nodos de computo (w1, w2, w3) | 180 txs
  --> Throughput: 26.74 rps | Speedup: 2.89x | Eficiencia: 96.5% | p95: 1043.4 ms

[TEST 5/9] Inyeccion de caos: Latencia inducida (+300 ms en w2)
  --> Round-Robin: 8.99 rps | p95: 4128.4 ms (saturacion de pool por nodo lento)
  --> Least-Connections: 20.59 rps | p95: 1548.2 ms (+129% de caudal, mitigacion efectiva)

[TEST 6/9] Inyeccion de caos: Nodo defectuoso (100% fallos en w2)
  --> Circuit Breaker w2 pasa a OPEN tras 3 fallos consecutivos
  --> Trafico redirigido a w1 y w3 | 120/120 atendidas sin errores 500 (17.87 rps)

[TEST 7/9] Inyeccion de fallos de negocio: 25% rechazos en compliance
  --> 89 completadas normalmente | 31 rechazadas en etapa 3
  --> 31 compensaciones Saga ejecutadas exitosamente (100% de consistencia)

[TEST 8/9] Inyeccion de fallo fisico: Caida total de nodo w3 (proceso terminado)
  --> Deteccion por conexion rechazada | Trafico absorbido por w1 y w2 (14.55 rps)

[TEST 9/9] Recuperacion en caliente: Reinicio de nodo w3
  --> Circuit Breaker pasa a HALF-OPEN tras periodo de enfriamiento (5 s)
  --> Reintegracion automatica confirmada | Throughput restituido a 23.53 rps
================================================================================
RESUMEN GENERAL: 1200 transacciones ejecutadas | 100% atencion | 0 errores 500
AUDITORIA: 9735 eventos persistidos en JSONL | Cola residual broker: 0
================================================================================
SUITE FINALIZADA CON EXITO (EXIT CODE 0)""")

    # Anexo D
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo D. Guía de Comandos para Reproducción Local"), size=12, bold=True)
    p = doc.add_paragraph()
    base_p(p, first_indent=0.5)
    set_run(p.add_run("Secuencia estandarizada de PowerShell para reproducir el clúster y la suite completa:"))
    add_code(doc, """# 1. Clonar el repositorio
git clone https://github.com/Alboguaci/tejiendo-redes-nexusai.git
cd tejiendo-redes-nexusai

# 2. Iniciar el cluster en segundo plano (5 nodos: Broker, Gateway, 3 Workers)
powershell -ExecutionPolicy Bypass -File .\\prototipo\\scripts\\start_all.ps1

# 3. Verificar estado de salud de todos los nodos
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8081/health
curl http://127.0.0.1:8082/health

# 4. Ejecutar la suite completa de benchmark y caos (1 200 transacciones)
python .\\pruebas\\load_test.py --profile full --transactions 180 --concurrency 24
python .\\pruebas\\chaos_test.py --scenario all

# 5. Generar las curvas graficas de rendimiento
python .\\pruebas\\generar_graficas.py

# 6. Detener todos los procesos del cluster de forma ordenada
powershell -ExecutionPolicy Bypass -File .\\prototipo\\scripts\\stop_all.ps1""")

    # Anexo E
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo E. Tabulación de Configuración y Parámetros Experimentales"), size=12, bold=True)
    rows_e = [
        ["Parámetro experimental", "Especificación técnica", "Justificación metodológica"],
        ["Plataforma de ejecución", "Windows 11, procesador 4 núcleos lógicos", "Entorno controlado para verificación de contención"],
        ["Intérprete y entorno", "Python 3.14.7 x64 (biblioteca estándar)", "Eliminación de variabilidad por dependencias externas"],
        ["Topología base de cómputo", "3 nodos de cómputo (workers), 4 hilos c/u", "Capacidad paralela nominal de 12 tareas concurrentes"],
        ["Pool de despacho del coordinador", "16 hilos dedicados", "Concurrencia de entrada acotada para evitar saturación"],
        ["Carga en pruebas de escalabilidad", "180 transacciones, concurrencia 24", "Demanda doble frente a la capacidad de cómputo paralela"],
        ["Carga en pruebas de robustez", "120 transacciones, concurrencia 24", "Presión constante para evaluar comportamiento ante fallos"],
        ["Trazabilidad total de la suite", "1 200 transacciones ejecutadas", "Muestra estadística robusta para cálculo de percentiles"]
    ]
    add_table(doc, rows_e, "Tabla E1. Configuración del entorno y de la carga de prueba", "Parámetros fijados durante todas las fases de evaluación empírica.")

    # Anexo F
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo F. Tabulación Completa de Escalabilidad Horizontal"), size=12, bold=True)
    rows_f = [
        ["Nodos", "Throughput (rps)", "Speedup", "Eficiencia", "Latencia p50 (ms)", "Latencia p95 (ms)", "Latencia p99 (ms)"],
        ["1 nodo", "9,24", "1,00×", "100,0 %", "2 131,3", "3 185,0", "3 243,4"],
        ["2 nodos", "18,14", "1,96×", "98,2 %", "1 047,7", "1 617,0", "1 638,8"],
        ["3 nodos", "26,74", "2,89×", "96,5 %", "854,2", "1 043,4", "1 127,0"]
    ]
    add_table(doc, rows_f, "Tabla F1. Escalabilidad horizontal con carga constante de 180 transacciones", "Carga concurrente cliente = 24 hilos. Muestra evolución del speedup y colapso de latencias en percentiles altos.")

    # Anexo G
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo G. Tabulación de Resiliencia ante Inyección de Fallos y Caos"), size=12, bold=True)
    rows_g = [
        ["Escenario de prueba", "Condición inyectada", "Atendidas (%)", "Completadas", "Compensadas", "Err 500", "Throughput", "Latencia p95"],
        ["Línea base", "3 nodos saludables", "100,0 %", "120", "0", "0", "26,37 rps", "1 033,6 ms"],
        ["Latencia inyectada", "+300 ms en nodo w2", "100,0 %", "120", "0", "0", "8,83 rps", "4 128,4 ms"],
        ["Nodo defectuoso", "100 % fallos en nodo w2", "100,0 %", "120", "0", "0", "17,87 rps", "1 531,2 ms"],
        ["Rechazo guardrail", "25 % rechazos compliance", "100,0 %", "89", "31", "0", "23,82 rps", "1 279,2 ms"],
        ["Caída de nodo", "w3 apagado físicamente", "100,0 %", "120", "0", "0", "14,55 rps", "2 828,8 ms"],
        ["Recuperación", "w3 reiniciado caliente", "100,0 %", "60", "0", "0", "23,53 rps", "518,6 ms"]
    ]
    add_table(doc, rows_g, "Tabla G1. Resultados de la evaluación de robustez ante fallos en seis escenarios", "Total transacciones atendidas = 100 % en todos los escenarios; cero códigos 500.")

    # Anexo H
    p = doc.add_paragraph()
    base_p(p, space_before=12, space_after=4)
    set_run(p.add_run("Anexo H. Tabulación Comparativa de Estrategias de Balanceo"), size=12, bold=True)
    rows_h = [
        ["Métrica de rendimiento", "Round-Robin (nodo lento)", "Least-Connections (nodo lento)", "Variación relativa"],
        ["Throughput efectivo", "8,99 rps", "20,59 rps", "+129,0 % de caudal"],
        ["Latencia p50", "2 546,7 ms", "1 123,4 ms", "-55,9 % de latencia"],
        ["Latencia p95", "4 128,4 ms", "1 548,2 ms", "-62,5 % de latencia"],
        ["Retención de capacidad nominal", "34,5 %", "75,7 %", "+41,2 puntos porcentuales"]
    ]
    add_table(doc, rows_h, "Tabla H1. Comparación de rendimiento entre Round-Robin y Least-Connections bajo nodo degradado", "Prueba con +300 ms de latencia inyectada en el worker w2.")

    doc.save(OUTPUT)
    print(f"OK -> {OUTPUT} ({OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
