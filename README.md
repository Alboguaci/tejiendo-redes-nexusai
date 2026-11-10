# Tejiendo redes: Arquitectura de software entre hilos y nodos

**Actividad 4 — Unidad 2 · Arquitectura de Software · CETO 2026**

Prototipo distribuido real de **NexusAI 2.0**, la evolución ejecutable de la arquitectura
cloud-native diseñada en la Actividad 2. El sistema demuestra, con procesos independientes
y mediciones reproducibles, cómo una arquitectura basada en **hilos y nodos** escala de forma
horizontal y se degrada de manera controlada cuando un nodo falla.

| Integrante | Rol |
|---|---|
| Juan Carlos Benítez Rojas | Líder de proyecto y arquitecto de software |
| Juan José Córdoba Eraso | Desarrollador y evaluador de calidad |

---

## Entregables

| Entregable | Ubicación |
|---|---|
| Repositorio del código | <https://github.com/Alboguaci/tejiendo-redes-nexusai> |
| Informe APA 7 (61 páginas) | [`informe/Informe_Actividad4_Tejiendo_Redes.pdf`](informe/Informe_Actividad4_Tejiendo_Redes.pdf) |
| Informe editable | [`informe/Informe_Actividad4_Tejiendo_Redes.docx`](informe/Informe_Actividad4_Tejiendo_Redes.docx) |
| Diagramas UML (componentes, secuencia, despliegue) | [`diagramas/`](diagramas/) |
| Prototipo ejecutable | [`prototipo/`](prototipo/) |
| Resultados, gráficas y evidencias | [`pruebas/`](pruebas/), [`evidencias/`](evidencias/) |
| Guion del video | [`guion_video.md`](guion_video.md) |
| Video demostrativo (YouTube, no listado) | Pendiente de publicar |

---

## Arquitectura en 30 segundos

```
cliente concurrente ──▶ Nodo 1 · coordinator.py :8080
                        API Gateway + Saga orquestada + Circuit Breaker
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     Nodo 3 · worker :8101  Nodo 4 · worker :8102  Nodo 5 · worker :8103
     ThreadPool(4)          ThreadPool(4)          ThreadPool(4)
              └─────────────────────┼─────────────────────┘
                                    ▼
                        Nodo 2 · broker.py :8090
                        topics + log de auditoría JSONL
                                    │
                                    ▼
                        dashboard.html :8088  (observabilidad)
```

Patrones implementados y justificados en el informe: **Saga orquestada**, **Broker/Event Bus**,
**Mediator**, **Proxy/API Gateway**, **Circuit Breaker**, **Bulkhead**, **Observer distribuido**,
**Strategy** y **Retry**.

---

## Ejecución rápida

Requiere Python 3.11+ (probado en 3.14.7). Solo biblioteca estándar para el clúster.

```bash
cd prototipo
python run_cluster.py --workers 3 --threads 16 --worker-threads 4
```

- Dashboard: <http://127.0.0.1:8088/dashboard.html>
- Carga: `python load_test.py --tasks 120 --concurrency 24`
- Fallos: `python chaos_test.py fail --worker http://127.0.0.1:8102 --rate 1.0`
- Suite completa: `python benchmark.py`

> Usar `127.0.0.1` en lugar de `localhost`: en el equipo de pruebas la resolución de
> `localhost` añadía ~2 042 ms por petición (951,5× más lenta).

Instrucciones detalladas, contratos HTTP y resultados completos en
[`prototipo/README.md`](prototipo/README.md).

---

## Resultados destacados

| Métrica | 1 nodo | 2 nodos | 3 nodos |
|---|---:|---:|---:|
| Throughput | 9,24 rps | 18,14 rps | 26,74 rps |
| Speedup | 1,00× | 1,96× | 2,89× |
| Eficiencia | 100,0 % | 98,2 % | 96,5 % |
| p95 | 3 185 ms | 1 617 ms | 1 043 ms |

- **Robustez:** 6 escenarios de caos, 100 % de tareas atendidas, 0 errores de sistema.
- **Trazabilidad:** 9 735 eventos publicados = consumidos, 0 descartes, cola en 0.
- **Balanceo:** least-connections conserva 75,7 % del throughput con un nodo lento,
  frente a 34,5 % de round-robin.

Detalle en [`pruebas/resumen.md`](pruebas/resumen.md).

---

## Estructura

```
Actividad4_Tejiendo_Redes/
├── informe/      Informe APA 7 (.docx, .pdf) y fuentes del documento
├── diagramas/    Tres diagramas PlantUML (.puml, .png, .svg) + renderizador
├── prototipo/    Clúster distribuido en Python (9 módulos + dashboard)
├── pruebas/      Suite de benchmark, resultados JSON y gráficas
├── evidencias/   Capturas para el informe y el video
└── guion_video.md
```

Corporación Escuela Tecnológica del Oriente · Ingeniería de Software · 2026.
