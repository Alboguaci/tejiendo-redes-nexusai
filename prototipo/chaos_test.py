"""Herramientas de inyeccion de fallos (Chaos Engineering) para NexusAI 2.0.

Permite degradar un nodo sin detenerlo (latencia / tasa de fallo), apagar un
nodo por completo y forzar fallos de negocio para observar la compensacion
de la Saga. Se usa desde ``benchmark.py`` y tambien por CLI para la demo.
"""

from __future__ import annotations

import argparse
import json

from common import http_json

DEFAULT_WORKERS = (
    "http://127.0.0.1:8101",
    "http://127.0.0.1:8102",
    "http://127.0.0.1:8103",
)


def set_chaos(url: str, latency_ms: int | None = None, fail_rate: float | None = None) -> dict:
    body = {}
    if latency_ms is not None:
        body["latency_ms"] = latency_ms
    if fail_rate is not None:
        body["fail_rate"] = fail_rate
    return http_json(url.rstrip("/") + "/chaos", "POST", body, timeout=5)


def reset_chaos(urls=DEFAULT_WORKERS) -> list[dict]:
    return [set_chaos(url, latency_ms=0, fail_rate=0.0) for url in urls]


def stop_node(url: str) -> bool:
    try:
        http_json(url.rstrip("/") + "/shutdown", "POST", {}, timeout=3)
        return True
    except Exception:
        return False


def guardrail_demo(coordinator_url: str, tasks: int = 10, rate: float = 0.4) -> dict:
    from load_test import imprimir, run_load

    result = run_load(coordinator_url, tasks=tasks, concurrency=4, force_fail_rate=rate)
    imprimir(result, "guardrail / compensacion")
    return result


def main():
    parser = argparse.ArgumentParser(description="Chaos toolkit NexusAI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_lat = sub.add_parser("latency", help="inyectar latencia en un nodo")
    p_lat.add_argument("--worker", default="http://127.0.0.1:8102")
    p_lat.add_argument("--ms", type=int, default=300)

    p_fail = sub.add_parser("fail", help="inyectar tasa de fallo en un nodo")
    p_fail.add_argument("--worker", default="http://127.0.0.1:8102")
    p_fail.add_argument("--rate", type=float, default=1.0)

    p_reset = sub.add_parser("reset", help="limpiar caos en todos los nodos")
    p_reset.add_argument("--workers", default=",".join(DEFAULT_WORKERS))

    p_stop = sub.add_parser("stop", help="apagar un nodo")
    p_stop.add_argument("--worker", default="http://127.0.0.1:8103")

    p_guard = sub.add_parser("guardrail", help="forzar fallos de negocio")
    p_guard.add_argument("--url", default="http://127.0.0.1:8080")
    p_guard.add_argument("--tasks", type=int, default=10)
    p_guard.add_argument("--rate", type=float, default=0.4)

    args = parser.parse_args()

    if args.command == "latency":
        print(json.dumps(set_chaos(args.worker, latency_ms=args.ms), indent=2))
    elif args.command == "fail":
        print(json.dumps(set_chaos(args.worker, fail_rate=args.rate), indent=2))
    elif args.command == "reset":
        urls = [url for url in args.workers.split(",") if url]
        print(json.dumps(reset_chaos(urls), indent=2))
    elif args.command == "stop":
        print("nodo apagado" if stop_node(args.worker) else "no fue posible apagar el nodo")
    elif args.command == "guardrail":
        guardrail_demo(args.url, args.tasks, args.rate)


if __name__ == "__main__":
    main()
