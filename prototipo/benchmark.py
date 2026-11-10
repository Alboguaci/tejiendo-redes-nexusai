"""Suite de evaluacion de NexusAI 2.0.

Ejecuta, sobre un cluster real de procesos independientes:

1. Escalabilidad horizontal: 1, 2 y 3 nodos de computo con la misma carga.
2. Robustez: latencia inyectada, nodo defectuoso, fallo de guardrail
   (compensacion Saga), caida total de un nodo y recuperacion.

Genera ``pruebas/resultados.json``, ``pruebas/resumen.md`` y las graficas
en ``pruebas/graficas``.
"""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from chaos_test import reset_chaos, set_chaos
from cluster import Cluster
from load_test import imprimir, run_load

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
PRUEBAS = PROJECT / "pruebas"
GRAFICAS = PRUEBAS / "graficas"

COLOR = {
    "primary": "#2C3E50",
    "accent": "#E67E22",
    "green": "#27AE60",
    "red": "#C0392B",
    "gray": "#95A5A6",
    "blue": "#2980B9",
}


def _seed(name: str) -> int:
    return sum(ord(char) for char in name)


def escenario(
    cluster: Cluster,
    name: str,
    description: str,
    tasks: int,
    concurrency: int,
    force_fail_rate: float = 0.0,
    reset_breakers: bool = True,
) -> dict:
    cluster.reset() if reset_breakers else _reset_metrics_only(cluster)
    result = run_load(
        cluster.coordinator_url,
        tasks=tasks,
        concurrency=concurrency,
        force_fail_rate=force_fail_rate,
        seed=_seed(name),
    )
    metrics = cluster.metrics()
    broker = cluster.broker_metrics()

    result["name"] = name
    result["description"] = description
    result["coordinator"] = {
        key: metrics.get(key)
        for key in (
            "total_tasks",
            "completed",
            "rolled_back",
            "rejected",
            "handled_rate_pct",
            "completion_rate_pct",
            "throughput_rps",
            "latency_ms",
            "steps",
            "workers",
        )
    }
    result["broker"] = {
        "total_published": broker.get("total_published"),
        "total_consumed": broker.get("total_consumed"),
        "dropped": broker.get("dropped"),
        "audit": broker.get("audit"),
        "topics": broker.get("topics"),
    }
    imprimir(result, f"{name} ({description})")
    return result


def _reset_metrics_only(cluster: Cluster):
    from common import http_json

    http_json(cluster.coordinator_url + "/reset", "POST", {"breakers": False}, timeout=10)


def grafica_escalabilidad(escalabilidad: list[dict]):
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    nodos = [item["config"]["nodes"] for item in escalabilidad]
    throughput = [item["summary"]["throughput_rps"] for item in escalabilidad]

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    bars = ax.bar([str(n) for n in nodos], throughput, color=COLOR["primary"], width=0.55)
    for bar, value in zip(bars, throughput):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.6,
            f"{value:.1f} rps",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    if throughput:
        ideal = [throughput[0] * n for n in nodos]
        ax.plot([str(n) for n in nodos], ideal, "o--", color=COLOR["accent"], label="escalado lineal ideal")
        ax.legend(frameon=False)
    ax.set_title("Escalabilidad horizontal: throughput vs. nodos de computo", fontsize=11, fontweight="bold")
    ax.set_xlabel("Nodos de computo activos")
    ax.set_ylabel("Transacciones por segundo")
    ax.set_ylim(0, max(throughput + [1]) * 1.35)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "01_escalabilidad_throughput.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    import numpy as np

    x = np.arange(len(nodos))
    width = 0.26
    series = [
        ("p50", [item["summary"]["latency_ms"]["p50"] for item in escalabilidad], COLOR["green"]),
        ("p95", [item["summary"]["latency_ms"]["p95"] for item in escalabilidad], COLOR["accent"]),
        ("p99", [item["summary"]["latency_ms"]["p99"] for item in escalabilidad], COLOR["red"]),
    ]
    for offset, (label, values, color) in zip((-width, 0, width), series):
        ax.bar(x + offset, values, width, label=label, color=color)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n} nodo(s)" for n in nodos])
    ax.set_title("Latencia extremo a extremo por cantidad de nodos", fontsize=11, fontweight="bold")
    ax.set_ylabel("Milisegundos")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "02_escalabilidad_latencia.png")
    plt.close(fig)


def grafica_robustez(robustez: list[dict]):
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    etiquetas = [item["short"] for item in robustez]
    handled = [item["summary"]["handled_rate_pct"] for item in robustez]
    completion = [item["summary"]["completion_rate_pct"] for item in robustez]
    p95 = [item["summary"]["latency_ms"]["p95"] for item in robustez]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=160)

    import numpy as np

    x = np.arange(len(etiquetas))
    width = 0.36
    ax1.bar(x - width / 2, handled, width, label="atendidas (200+409)", color=COLOR["blue"])
    ax1.bar(x + width / 2, completion, width, label="completadas (200)", color=COLOR["green"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, rotation=18, ha="right", fontsize=9)
    ax1.set_ylim(0, 110)
    ax1.set_ylabel("Porcentaje de transacciones")
    ax1.set_title("Tasa de atencion bajo fallos", fontsize=11, fontweight="bold")
    ax1.legend(frameon=False, fontsize=9)
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    bars = ax2.bar(x, p95, color=COLOR["accent"], width=0.55)
    for bar, value in zip(bars, p95):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(p95 + [1]) * 0.02,
            f"{value:.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax2.set_xticks(x)
    ax2.set_xticklabels(etiquetas, rotation=18, ha="right", fontsize=9)
    ax2.set_ylabel("Latencia p95 (ms)")
    ax2.set_title("Impacto en latencia p95", fontsize=11, fontweight="bold")
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(GRAFICAS / "03_robustez.png")
    plt.close(fig)


def grafica_pasos(base: dict):
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    steps = base["coordinator"]["steps"]
    nombres = [name for name in ("triage", "rag", "compliance", "compensate") if name in steps]
    promedios = [steps[name]["avg"] for name in nombres]
    p95 = [steps[name]["p95"] for name in nombres]

    import numpy as np

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=160)
    x = np.arange(len(nombres))
    ax.bar(x - 0.18, promedios, 0.36, label="promedio", color=COLOR["primary"])
    ax.bar(x + 0.18, p95, 0.36, label="p95", color=COLOR["gray"])
    for index, value in enumerate(promedios):
        ax.text(index - 0.18, value + 3, f"{value:.0f}", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_ylabel("Milisegundos")
    ax.set_title("Costo por paso de la Saga (linea base, 3 nodos)", fontsize=11, fontweight="bold")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "04_latencia_por_paso.png")
    plt.close(fig)


def escribir_resumen(escenarios: list[dict], metadata: dict):
    lineas = [
        "# Resumen de resultados - NexusAI 2.0",
        "",
        f"- Fecha de ejecucion: {metadata['timestamp']}",
        f"- Equipo: {metadata['platform']} | CPU logicos: {metadata['cpu_count']} | Python {metadata['python']}",
        f"- Hilos por nodo de computo: {metadata['worker_threads']} | "
        f"Hilos del pool de despacho: {metadata['coordinator_threads']} | "
        f"Estrategia: {metadata['strategy']}",
        "",
        "## Escenarios",
        "",
        "| Escenario | Tareas | Concurrencia | Throughput (rps) | p50 (ms) | p95 (ms) | p99 (ms) | Completadas | Compensadas | Errores |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in escenarios:
        s = item["summary"]
        lineas.append(
            f"| {item['name']} | {s['tasks']} | {item['config']['concurrency']} | "
            f"{s['throughput_rps']:.2f} | {s['latency_ms']['p50']:.1f} | "
            f"{s['latency_ms']['p95']:.1f} | {s['latency_ms']['p99']:.1f} | "
            f"{s['completed']} | {s['rolled_back']} | {s['errors']} |"
        )

    lineas += ["", "## Escalabilidad horizontal", "", "| Nodos | Throughput (rps) | Speedup | Eficiencia |", "|---:|---:|---:|---:|"]
    base = next((item for item in escenarios if item["name"] == "escalabilidad_1_nodo"), None)
    for item in escenarios:
        if not item["name"].startswith("escalabilidad_"):
            continue
        nodes = item["config"]["nodes"]
        speedup = item["summary"]["throughput_rps"] / base["summary"]["throughput_rps"] if base else 0
        lineas.append(
            f"| {nodes} | {item['summary']['throughput_rps']:.2f} | "
            f"{speedup:.2f}x | {speedup / nodes * 100:.1f}% |"
        )

    (PRUEBAS / "resumen.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    PRUEBAS.mkdir(parents=True, exist_ok=True)
    GRAFICAS.mkdir(parents=True, exist_ok=True)

    cluster = Cluster(workers=3, worker_threads=4, coordinator_threads=16)
    escenarios: list[dict] = []
    escalabilidad: list[dict] = []
    robustez: list[dict] = []

    # Cada corrida debe partir de una bitacora limpia para que las cifras
    # del informe correspondan exactamente a este experimento.
    for stale in (PRUEBAS / "event_log.jsonl",):
        if stale.exists():
            stale.unlink()

    print("[benchmark] iniciando cluster (broker + 3 nodos + coordinador)...", flush=True)
    cluster.start()
    print(f"[benchmark] dashboard: {cluster.dashboard_url}", flush=True)

    try:
        print("[benchmark] calentamiento...", flush=True)
        run_load(cluster.coordinator_url, tasks=12, concurrency=4, seed=1)

        # ---------------- Escalabilidad horizontal ----------------
        for nodes in (1, 2, 3):
            cluster.set_active_workers(nodes)
            time.sleep(0.3)
            item = escenario(
                cluster,
                f"escalabilidad_{nodes}_nodo" + ("s" if nodes > 1 else ""),
                f"{nodes} nodo(s) de computo con la misma carga",
                tasks=180,
                concurrency=24,
            )
            item["config"]["nodes"] = nodes
            escalabilidad.append(item)
            escenarios.append(item)

        cluster.set_active_workers(3)

        # ---------------- Robustez ----------------
        base = escenario(
            cluster,
            "robustez_linea_base",
            "3 nodos sin fallos inyectados",
            tasks=120,
            concurrency=24,
        )
        base["short"] = "Linea base"
        robustez.append(base)
        escenarios.append(base)

        set_chaos(cluster.worker_urls[1], latency_ms=300)
        latencia = escenario(
            cluster,
            "robustez_latencia_w2",
            "300 ms de latencia inyectada en el nodo w2",
            tasks=120,
            concurrency=24,
        )
        latencia["short"] = "Latencia w2"
        robustez.append(latencia)
        escenarios.append(latencia)
        reset_chaos(cluster.worker_urls)

        set_chaos(cluster.worker_urls[1], fail_rate=1.0)
        defectuoso = escenario(
            cluster,
            "robustez_nodo_defectuoso_w2",
            "w2 falla el 100% de sus peticiones (Circuit Breaker)",
            tasks=120,
            concurrency=24,
        )
        defectuoso["short"] = "Nodo defectuoso"
        robustez.append(defectuoso)
        escenarios.append(defectuoso)
        reset_chaos(cluster.worker_urls)

        guardrail = escenario(
            cluster,
            "robustez_guardrail",
            "25% de transacciones rechazadas por guardrail (compensacion Saga)",
            tasks=120,
            concurrency=24,
            force_fail_rate=0.25,
        )
        guardrail["short"] = "Guardrail"
        robustez.append(guardrail)
        escenarios.append(guardrail)

        cluster.stop_worker(2)
        time.sleep(1.0)
        caida = escenario(
            cluster,
            "robustez_caida_w3",
            "w3 apagado por completo durante la carga",
            tasks=120,
            concurrency=24,
        )
        caida["short"] = "Nodo caido"
        robustez.append(caida)
        escenarios.append(caida)

        cluster.start_worker(2)
        time.sleep(6.0)
        recuperacion = escenario(
            cluster,
            "robustez_recuperacion_w3",
            "w3 reiniciado; el Circuit Breaker vuelve a enrutar trafico",
            tasks=60,
            concurrency=12,
            reset_breakers=False,
        )
        recuperacion["short"] = "Recuperacion"
        recuperacion["w3_successes"] = next(
            (w["successes"] for w in recuperacion["coordinator"]["workers"] if w["id"] == "w3"),
            0,
        )
        robustez.append(recuperacion)
        escenarios.append(recuperacion)

        # ---------------- Artefactos ----------------
        metadata = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": f"{platform.system()} {platform.release()}",
            "python": platform.python_version(),
            "cpu_count": __import__("os").cpu_count(),
            "worker_threads": cluster.worker_threads,
            "coordinator_threads": cluster.coordinator_threads,
            "strategy": cluster.strategy,
            "workers": cluster.workers,
        }
        payload = {"metadata": metadata, "escenarios": escenarios}
        (PRUEBAS / "resultados.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        escribir_resumen(escenarios, metadata)
        grafica_escalabilidad(escalabilidad)
        grafica_robustez(robustez)
        grafica_pasos(base)

        print("\n[benchmark] artefactos generados:", flush=True)
        for path in sorted(PRUEBAS.glob("*")):
            if path.is_file():
                print(f"  - {path.name}", flush=True)
        for path in sorted(GRAFICAS.glob("*.png")):
            print(f"  - graficas/{path.name}", flush=True)
    finally:
        print("[benchmark] deteniendo cluster...", flush=True)
        cluster.stop()


if __name__ == "__main__":
    main()
