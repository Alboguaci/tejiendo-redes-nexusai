# Resumen de resultados - NexusAI 2.0

- Fecha de ejecucion: 2026-11-09 18:46:38
- Equipo: Windows 11 | CPU logicos: 4 | Python 3.14.7
- Hilos por nodo de computo: 4 | Hilos del pool de despacho: 16 | Estrategia: round-robin

## Escenarios

| Escenario | Tareas | Concurrencia | Throughput (rps) | p50 (ms) | p95 (ms) | p99 (ms) | Completadas | Compensadas | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| escalabilidad_1_nodo | 180 | 24 | 9.24 | 2131.3 | 3185.0 | 3243.4 | 180 | 0 | 0 |
| escalabilidad_2_nodos | 180 | 24 | 18.14 | 1047.7 | 1617.0 | 1638.8 | 180 | 0 | 0 |
| escalabilidad_3_nodos | 180 | 24 | 26.74 | 854.2 | 1043.4 | 1127.0 | 180 | 0 | 0 |
| robustez_linea_base | 120 | 24 | 26.37 | 843.5 | 1033.6 | 1099.5 | 120 | 0 | 0 |
| robustez_latencia_w2 | 120 | 24 | 8.83 | 2546.7 | 4128.4 | 4945.4 | 120 | 0 | 0 |
| robustez_nodo_defectuoso_w2 | 120 | 24 | 17.87 | 1258.3 | 1531.2 | 1624.0 | 120 | 0 | 0 |
| robustez_guardrail | 120 | 24 | 23.82 | 913.9 | 1279.2 | 1377.5 | 89 | 31 | 0 |
| robustez_caida_w3 | 120 | 24 | 14.55 | 1323.5 | 2828.8 | 3453.5 | 120 | 0 | 0 |
| robustez_recuperacion_w3 | 60 | 12 | 23.53 | 470.6 | 518.6 | 570.4 | 60 | 0 | 0 |

## Escalabilidad horizontal

| Nodos | Throughput (rps) | Speedup | Eficiencia |
|---:|---:|---:|---:|
| 1 | 9.24 | 1.00x | 100.0% |
| 2 | 18.14 | 1.96x | 98.2% |
| 3 | 26.74 | 2.89x | 96.5% |
