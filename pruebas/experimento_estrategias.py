"""Compara las estrategias de balanceo bajo un nodo degradado.

Experimento de apoyo al informe: con la misma carga y el mismo fallo
(300 ms de latencia en w2), compara round-robin contra least-connections.
El objetivo es demostrar que la estrategia de balanceo no es un detalle de
implementacion: cambia el throughput y la latencia percibida.

Salida: pruebas/estrategias.json y pruebas/graficas/05_estrategias.png
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROTOTIPO = Path(__file__).resolve().parent.parent / "prototipo"
sys.path.insert(0, str(PROTOTIPO))

from chaos_test import reset_chaos, set_chaos
from cluster import Cluster
from load_test import imprimir, run_load

PRUEBAS = Path(__file__).resolve().parent.parent / "pruebas"
GRAFICAS = PRUEBAS / "graficas"
TASKS = 120
CONCURRENCY = 24


def correr(strategy: str) -> dict:
    cluster = Cluster(workers=3, worker_threads=4, coordinator_threads=16, strategy=strategy)
    print(f"\n[estrategias] iniciando cluster con {strategy}...", flush=True)
    cluster.start()
    try:
        run_load(cluster.coordinator_url, tasks=12, concurrency=4, seed=1)
        cluster.reset()
        base = run_load(cluster.coordinator_url, tasks=TASKS, concurrency=CONCURRENCY, seed=11)
        imprimir(base, f"{strategy} / linea base")

        set_chaos(cluster.worker_urls[1], latency_ms=300)
        cluster.reset()
        lento = run_load(cluster.coordinator_url, tasks=TASKS, concurrency=CONCURRENCY, seed=11)
        imprimir(lento, f"{strategy} / w2 con +300 ms")
        reset_chaos(cluster.worker_urls)
        metrics = cluster.metrics()
    finally:
        cluster.stop()

    return {
        "strategy": strategy,
        "baseline": base["summary"],
        "slow_node": lento["summary"],
        "workers": metrics.get("workers"),
    }


def graficar(resultados: list[dict]):
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    etiquetas = [item["strategy"] for item in resultados]
    base = [item["baseline"]["throughput_rps"] for item in resultados]
    lento = [item["slow_node"]["throughput_rps"] for item in resultados]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.2), dpi=160)
    x = np.arange(len(etiquetas))
    width = 0.34
    ax1.bar(x - width / 2, base, width, label="sin fallo", color="#2C3E50")
    ax1.bar(x + width / 2, lento, width, label="w2 +300 ms", color="#E67E22")
    for offset, values in ((-width / 2, base), (width / 2, lento)):
        for pos, value in zip(x + offset, values):
            ax1.text(pos, value + 0.5, f"{value:.1f}", ha="center", fontsize=9, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas)
    ax1.set_ylabel("Transacciones por segundo")
    ax1.set_title("Throughput segun estrategia de balanceo", fontsize=11, fontweight="bold")
    ax1.legend(frameon=False, fontsize=9)
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_ylim(0, max(base + lento) * 1.28)

    p95_base = [item["baseline"]["latency_ms"]["p95"] for item in resultados]
    p95_lento = [item["slow_node"]["latency_ms"]["p95"] for item in resultados]
    ax2.bar(x - width / 2, p95_base, width, label="sin fallo", color="#2980B9")
    ax2.bar(x + width / 2, p95_lento, width, label="w2 +300 ms", color="#C0392B")
    ax2.set_xticks(x)
    ax2.set_xticklabels(etiquetas)
    ax2.set_ylabel("Latencia p95 (ms)")
    ax2.set_title("Latencia p95 segun estrategia de balanceo", fontsize=11, fontweight="bold")
    ax2.legend(frameon=False, fontsize=9)
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(GRAFICAS / "05_estrategias.png")
    plt.close(fig)


def main():
    resultados = []
    for strategy in ("round-robin", "least-connections"):
        resultados.append(correr(strategy))

    for item in resultados:
        base = item["baseline"]["throughput_rps"]
        lento = item["slow_node"]["throughput_rps"]
        item["degradacion_pct"] = round((1 - lento / base) * 100.0, 2)

    payload = {"tasks": TASKS, "concurrency": CONCURRENCY, "resultados": resultados}
    (PRUEBAS / "estrategias.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    graficar(resultados)

    print("\n=== Comparacion de estrategias ===")
    for item in resultados:
        print(
            f"{item['strategy']:>18}: base={item['baseline']['throughput_rps']:>6.2f} rps  "
            f"lento={item['slow_node']['throughput_rps']:>6.2f} rps  "
            f"degradacion={item['degradacion_pct']:>5.1f}%  "
            f"p95_lento={item['slow_node']['latency_ms']['p95']:>7.1f} ms"
        )


if __name__ == "__main__":
    main()
