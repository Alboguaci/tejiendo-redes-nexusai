"""Demo interactiva: levanta el cluster completo y lo deja corriendo.

Uso:
    python run_cluster.py --workers 3 --threads 16 --worker-threads 4

Luego abrir:
    http://127.0.0.1:8088/dashboard.html
"""

from __future__ import annotations

import argparse
import time

from cluster import Cluster


def main():
    parser = argparse.ArgumentParser(description="Cluster demo NexusAI 2.0")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--worker-threads", type=int, default=4)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--strategy", default="round-robin")
    args = parser.parse_args()

    cluster = Cluster(
        workers=args.workers,
        worker_threads=args.worker_threads,
        coordinator_threads=args.threads,
        strategy=args.strategy,
    )

    print("[run_cluster] iniciando nodos...", flush=True)
    cluster.start()
    print(
        "\n"
        "  NexusAI 2.0 en ejecucion\n"
        "  ------------------------\n"
        f"  API Gateway / Coordinador : {cluster.coordinator_url}\n"
        f"  Message Broker            : {cluster.broker_url}\n"
        f"  Dashboard                 : {cluster.dashboard_url}\n"
        + "".join(
            f"  Worker {index + 1}                 : {url}\n"
            for index, url in enumerate(cluster.worker_urls)
        )
        + "\n  Prueba rapida:\n"
        f'    python load_test.py --tasks 60 --concurrency 12\n'
        "\n  Ctrl+C para detener el cluster.\n",
        flush=True,
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[run_cluster] deteniendo...", flush=True)
    finally:
        cluster.stop()


if __name__ == "__main__":
    main()
