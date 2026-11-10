"""Generador de carga concurrente para NexusAI 2.0.

Abre ``concurrency`` clientes simultaneos y reparte ``tasks`` transacciones
Saga completas (POST /task). Mide latencia extremo a extremo y clasifica la
respuesta: 200 completada, 409 compensada, otro -> error de sistema.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import http_json_status, percentile

CANALES = ("web", "app", "whatsapp", "call-center")
INTENCIONES = (
    "consultar estado de pedido",
    "escalar incidente critico",
    "resumir contrato de servicio",
    "validar cumplimiento normativo",
)


def _pct(values, p):
    return round(percentile(values, p), 2)


def resumir(muestras: list[dict], wall_time_s: float) -> dict:
    ok = [m for m in muestras if m["status"] == 200]
    rolled = [m for m in muestras if m["status"] == 409]
    errors = [m for m in muestras if m["status"] not in (200, 409)]
    latencias = [m["latency_ms"] for m in muestras]
    handled = len(ok) + len(rolled)
    total = len(muestras)
    return {
        "tasks": total,
        "completed": len(ok),
        "rolled_back": len(rolled),
        "errors": len(errors),
        "handled_rate_pct": round(handled / total * 100.0, 2) if total else 0.0,
        "completion_rate_pct": round(len(ok) / total * 100.0, 2) if total else 0.0,
        "wall_time_s": round(wall_time_s, 3),
        "throughput_rps": round(handled / wall_time_s, 2) if wall_time_s else 0.0,
        "latency_ms": {
            "avg": round(sum(latencias) / len(latencias), 2) if latencias else 0.0,
            "p50": _pct(latencias, 50),
            "p95": _pct(latencias, 95),
            "p99": _pct(latencias, 99),
            "max": round(max(latencias), 2) if latencias else 0.0,
        },
        "latency_ok_ms": {
            "p50": _pct([m["latency_ms"] for m in ok], 50),
            "p95": _pct([m["latency_ms"] for m in ok], 95),
        },
        "status_counts": {
            "200": len(ok),
            "409": len(rolled),
            "other": len(errors),
        },
    }


def run_load(
    base_url: str,
    tasks: int = 120,
    concurrency: int = 24,
    force_fail_rate: float = 0.0,
    timeout: float = 180.0,
    seed: int | None = None,
) -> dict:
    base_url = base_url.rstrip("/")
    rng = random.Random(seed)
    lock = threading.Lock()
    counter = itertools.count()
    samples: list[dict] = []

    def client():
        while True:
            with lock:
                index = next(counter)
            if index >= tasks:
                return
            payload = {
                "prompt": f"{rng.choice(INTENCIONES)} #{index}",
                "canal": rng.choice(CANALES),
            }
            if force_fail_rate and rng.random() < force_fail_rate:
                payload["force_fail"] = True

            start = time.perf_counter()
            status, body = http_json_status(
                base_url + "/task", {"payload": payload}, timeout=timeout
            )
            elapsed = (time.perf_counter() - start) * 1000.0
            record = {
                "index": index,
                "status": status,
                "latency_ms": round(elapsed, 2),
                "saga_status": body.get("status"),
                "failed_step": body.get("failed_step"),
                "workers": [s.get("worker") for s in body.get("steps", [])],
            }
            with lock:
                samples.append(record)

    start_all = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="client") as pool:
        futures = [pool.submit(client) for _ in range(concurrency)]
        for future in futures:
            future.result()
    wall_time = time.perf_counter() - start_all

    samples.sort(key=lambda item: item["index"])
    return {
        "config": {
            "base_url": base_url,
            "tasks": tasks,
            "concurrency": concurrency,
            "force_fail_rate": force_fail_rate,
        },
        "summary": resumir(samples, wall_time),
        "samples": samples,
    }


def imprimir(resultado: dict, etiqueta: str = ""):
    s = resultado["summary"]
    print(f"\n=== {etiqueta or 'resultado'} ===")
    print(
        f"tareas={s['tasks']:>4}  ok={s['completed']:>4}  "
        f"compensadas={s['rolled_back']:>4}  errores={s['errors']:>3}"
    )
    print(
        f"throughput={s['throughput_rps']:>6.2f} rps   "
        f"wall={s['wall_time_s']:>6.2f}s   "
        f"handled={s['handled_rate_pct']:>6.2f}%"
    )
    lat = s["latency_ms"]
    print(
        f"latencia e2e: avg={lat['avg']:.1f}ms  p50={lat['p50']:.1f}ms  "
        f"p95={lat['p95']:.1f}ms  p99={lat['p99']:.1f}ms  max={lat['max']:.1f}ms"
    )


def main():
    parser = argparse.ArgumentParser(description="Generador de carga NexusAI")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--tasks", type=int, default=120)
    parser.add_argument("--concurrency", type=int, default=24)
    parser.add_argument("--force-fail-rate", type=float, default=0.0)
    parser.add_argument("--label", default="carga_manual")
    parser.add_argument("--output", default="")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    resultado = run_load(
        args.url,
        tasks=args.tasks,
        concurrency=args.concurrency,
        force_fail_rate=args.force_fail_rate,
        seed=args.seed,
    )
    imprimir(resultado, args.label)

    if args.output:
        destino = Path(args.output)
    else:
        destino = Path(__file__).resolve().parent.parent / "pruebas" / f"{args.label}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nresultados -> {destino}")


if __name__ == "__main__":
    main()
