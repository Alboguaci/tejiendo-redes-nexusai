# NexusAI 2.0 — Prototipo de arquitectura distribuida con hilos y nodos

**Actividad 4 · Tejiendo redes: Arquitectura de software entre hilos y nodos**
Unidad 2 — Patrones y diseño de arquitectura · Arquitectura de Software · CETO

Prototipo distribuido real (procesos independientes, no una simulación en el navegador)
que evoluciona la arquitectura cloud-native de NexusAI (Actividad 2) a una red de nodos
coordinados por una **Saga orquestada** sobre un **broker de eventos**, con
**Circuit Breaker**, **Bulkhead**, **Strategy** y **Retry**.

---

## 1. Arquitectura en una imagen

```
                        ┌──────────────────────────────┐
   load_test.py ───────▶│  Nodo 1 · API Gateway        │
   (clientes            │  coordinator.py      :8080   │
    concurrentes)       │  Saga + Circuit Breaker      │
                        │  Dispatch ThreadPool (16)    │
                        └───────┬───────────┬──────────┘
                                │           │
              ┌─────────────────┼───────────┼─────────────────┐
              ▼                 ▼           ▼                 │
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
      │ Nodo 3       │  │ Nodo 4       │  │ Nodo 5       │    │
      │ worker.py    │  │ worker.py    │  │ worker.py    │    │
      │ :8101 · 4 h. │  │ :8102 · 4 h. │  │ :8103 · 4 h. │    │
      └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
             │  publish(events)│                 │            │
             └─────────────────┼─────────────────┘            │
                               ▼                              │
                    ┌──────────────────────┐                  │
                    │ Nodo 2 · Broker      │                  │
                    │ broker.py     :8090  │                  │
                    │ topics + JSONL       │                  │
                    └──────────┬───────────┘                  │
                               ▼                              ▼
                    pruebas/event_log.jsonl      dashboard.html :8088
```

| Nodo | Proceso | Puerto | Responsabilidad |
|---|---|---|---|
| 1 | `coordinator.py` | 8080 | API Gateway, Saga orquestada, balanceo, Circuit Breaker |
| 2 | `broker.py` | 8090 | Bus de eventos (topics) + log de auditoría JSONL |
| 3–5 | `worker.py` | 8101–8103 | Cómputo cognitivo por pasos, ThreadPool propio (Bulkhead) |
| 6 | `http.server` | 8088 | Dashboard operacional (Chart.js-free, canvas nativo) |

---

## 2. Requisitos

- Python **3.11+** (probado en 3.14.7). Solo biblioteca estándar para el clúster.
- Para el benchmark y las gráficas: `matplotlib` y `numpy`.

```bash
python -m pip install matplotlib numpy
```

> **Nota de reproducibilidad (Windows):** usar siempre `127.0.0.1` en lugar de
> `localhost`. En el equipo de pruebas la resolución de `localhost` añadía ~2 042 ms
> por petición frente a ~2 ms con `127.0.0.1`, una diferencia de 951,5× (ver
> `pruebas/resolucion_localhost.json`).

---

## 3. Ejecución rápida

### 3.1 Levantar el clúster (demo / video)

```bash
cd prototipo
python run_cluster.py --workers 3 --threads 16 --worker-threads 4
```

Abrir el dashboard: <http://127.0.0.1:8088/dashboard.html>

### 3.2 Generar carga

```bash
python load_test.py --tasks 120 --concurrency 24 --label carga_manual
```

### 3.3 Inyectar fallos (chaos)

```bash
python chaos_test.py latency --worker http://127.0.0.1:8102 --ms 300
python chaos_test.py fail    --worker http://127.0.0.1:8102 --rate 1.0
python chaos_test.py stop    --worker http://127.0.0.1:8103
python chaos_test.py reset
```

### 3.4 Suite completa de evaluación

```bash
python benchmark.py
```

Genera `pruebas/resultados.json`, `pruebas/resumen.md` y las gráficas en
`pruebas/graficas/`. El clúster se levanta y se detiene automáticamente.

### 3.5 Comparación de estrategias de balanceo

```bash
python ../pruebas/experimento_estrategias.py
```

Compara round-robin contra least-connections bajo un nodo lento y genera
`pruebas/estrategias.json` y `pruebas/graficas/05_estrategias.png`.

---

## 4. Contratos HTTP

| Método | Ruta | Nodo | Descripción |
|---|---|---|---|
| `POST` | `/task` | Coordinador | Ejecuta una Saga completa (200 / 409 / 503) |
| `GET` | `/metrics` | Coordinador | Throughput, percentiles, estado de nodos y sagas |
| `GET` | `/workers` | Coordinador | Estado de los nodos y del Circuit Breaker |
| `POST` | `/workers` | Coordinador | Habilita un subconjunto de nodos (pruebas de escalado) |
| `POST` | `/reset` | Coordinador | Reinicia métricas (`breakers=false` conserva el estado) |
| `POST` | `/execute` | Worker | Ejecuta un paso (`triage`, `rag`, `compliance`, `compensate`) |
| `POST` | `/chaos` | Worker | Inyecta `latency_ms` y/o `fail_rate` |
| `POST` | `/publish` | Broker | Publica un evento en un topic |
| `GET` | `/consume` | Broker | Consume el siguiente evento de un topic |
| `GET` | `/health` | Todos | Verificación de vida |

Respuestas de `/task`:

- **200** `{"status":"completed", "steps":[...]}` — Saga completada.
- **409** `{"status":"rolled_back", "failed_step":"compliance", "compensation":[...]}` — fallo de negocio con compensación inversa.
- **503 / error** — sin nodos disponibles (todos los breakers abiertos).

---

## 5. Patrones implementados

| Patrón | Dónde | Evidencia en código |
|---|---|---|
| **Saga orquestada** | `SagaOrchestrator` | `coordinator.py` → `run()` + `_compensate()` |
| **Broker / Event Bus** | Nodo 2 | `broker.py` → topics `events`, log JSONL |
| **Mediator** | Coordinador | Los nodos no se conocen entre sí; solo hablan con el mediador |
| **Proxy / API Gateway** | `CoordinatorHandler` | Punto único de entrada `POST /task` |
| **Circuit Breaker** | `CircuitBreaker` | `coordinator.py` → CLOSED / OPEN / HALF_OPEN |
| **Bulkhead** | `ThreadPoolExecutor` por nodo | `worker.py` → `ThreadPool(4)` aislado |
| **Observer distribuido** | Eventos del broker | `saga.started`, `task.completed`, `saga.rolled_back` |
| **Strategy** | Balanceo | `RoundRobinStrategy` / `LeastConnectionsStrategy` |
| **Retry** | `WorkerPool.execute` | `max_attempts=2` sobre nodos distintos |

---

## 6. Resultados medidos (Windows 11, 4 CPU lógicos, Python 3.14.7)

**Escalabilidad horizontal** (180 tareas, concurrencia 24, round-robin):

| Nodos | Throughput | Speedup | Eficiencia | p50 | p95 | p99 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9,24 rps | 1,00× | 100,0 % | 2 131 ms | 3 185 ms | 3 243 ms |
| 2 | 18,14 rps | 1,96× | 98,2 % | 1 048 ms | 1 617 ms | 1 639 ms |
| 3 | 26,74 rps | 2,89× | 96,5 % | 854 ms | 1 043 ms | 1 127 ms |

**Robustez** (120 tareas, concurrencia 24, 3 nodos):

| Escenario | Atendidas | Throughput | p95 |
|---|---:|---:|---:|
| Línea base | 100 % | 26,37 rps | 1 034 ms |
| Latencia +300 ms en w2 | 100 % | 8,83 rps | 4 128 ms |
| w2 falla el 100 % (breaker OPEN) | 100 % | 17,87 rps | 1 531 ms |
| Guardrail (25 % rechazos) | 100 % (31 compensadas) | 23,82 rps | 1 279 ms |
| Caída total de w3 | 100 % | 14,55 rps | 2 829 ms |
| Recuperación de w3 | 100 % | 23,53 rps | 519 ms |

**Estrategia de balanceo bajo un nodo lento** (120 tareas, w2 con +300 ms):

| Estrategia | Base | Con w2 lento | Degradación | p95 con w2 lento |
|---|---:|---:|---:|---:|
| round-robin | 26,05 rps | 8,99 rps | 65,5 % | 4 178 ms |
| least-connections | 27,20 rps | 20,59 rps | 24,3 % | 2 224 ms |

**Broker y trazabilidad:** 9 735 eventos publicados = consumidos, 0 descartes,
profundidad de cola 0 al cierre de cada escenario. Tipos registrados por el
consumidor de auditoría: `saga.started` 1 212, `saga.step.completed` 3 605,
`task.completed` 3 667, `saga.completed` 1 180, `task.failed` 40 y
`saga.rolled_back` 31.

**Balance global de la suite:** 1 200 transacciones, 100 % atendidas, 0 errores
de sistema, 2 111 líneas de Python en 9 módulos.

Detalle completo en `pruebas/resumen.md`, `pruebas/resultados.json` y
`pruebas/estrategias.json`.

---

## 7. Estructura del repositorio

```
Actividad4_Tejiendo_Redes/
├── informe/            Informe APA 7 (.docx y .pdf) y fuentes
├── diagramas/          3 diagramas PlantUML (.puml, .png, .svg) + renderizador
├── prototipo/          Código del clúster distribuido
│   ├── common.py       Utilidades HTTP/JSON, percentiles
│   ├── broker.py       Nodo 2: broker de eventos
│   ├── worker.py       Nodos 3-5: workers con ThreadPool
│   ├── coordinator.py  Nodo 1: gateway + Saga + breaker + balanceo
│   ├── cluster.py      Orquestación de procesos del clúster
│   ├── load_test.py    Generador de carga concurrente
│   ├── chaos_test.py   Inyección de fallos
│   ├── benchmark.py    Suite de escalabilidad y robustez
│   ├── run_cluster.py  Demo interactiva
│   └── dashboard.html  Consola de monitoreo
├── pruebas/            Resultados, gráficas, logs y evidencias
└── evidencias/         Capturas para el informe y el video
```

---

## 8. Autores

- **Juan Carlos Benítez Rojas** — Líder de proyecto, arquitecto de software.
- **Juan José Córdoba Eraso** — Desarrollador, evaluador de calidad.

Corporación Escuela Tecnológica del Oriente · Ingeniería de Software · 2026.

---

## 9. Entregables

| Entregable | Ubicación |
|---|---|
| Repositorio del código | https://github.com/Alboguaci/tejiendo-redes-nexusai |
| Informe APA 7 (PDF) | `informe/Informe_Actividad4_Tejiendo_Redes.pdf` |
| Diagramas UML (PlantUML, PNG, SVG) | `diagramas/` |
| Prototipo ejecutable | `prototipo/` |
| Resultados y evidencias | `pruebas/`, `evidencias/` |
| Video demostrativo (YouTube, no listado) | Pendiente de publicar |
