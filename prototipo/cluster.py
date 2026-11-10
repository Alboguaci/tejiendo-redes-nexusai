"""Orquestacion del cluster local de NexusAI 2.0.

Levanta procesos independientes (nodos reales, no hilos simulados):

    broker.py       -> Nodo 2  (:8090)
    worker.py x N   -> Nodos 3.. (:8101, :8102, :8103)
    coordinator.py  -> Nodo 1  (:8080)
    http.server     -> Nodo 6  (:8088, dashboard estatico)
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from common import http_json, wait_for

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
PRUEBAS = PROJECT / "pruebas"
LOGS = PRUEBAS / "logs"
CREATE_NEW_PROCESS_GROUP = 0x00000200


class Cluster:
    def __init__(
        self,
        workers: int = 3,
        worker_threads: int = 4,
        coordinator_threads: int = 16,
        strategy: str = "round-robin",
        broker_port: int = 8090,
        coordinator_port: int = 8080,
        dashboard_port: int = 8088,
        worker_base_port: int = 8101,
    ):
        self.workers = workers
        self.worker_threads = worker_threads
        self.coordinator_threads = coordinator_threads
        self.strategy = strategy
        self.broker_port = broker_port
        self.coordinator_port = coordinator_port
        self.dashboard_port = dashboard_port
        self.worker_base_port = worker_base_port

        self.worker_urls = [
            f"http://127.0.0.1:{worker_base_port + index}" for index in range(workers)
        ]
        self.broker_url = f"http://127.0.0.1:{broker_port}"
        self.coordinator_url = f"http://127.0.0.1:{coordinator_port}"
        self.dashboard_url = f"http://127.0.0.1:{dashboard_port}/dashboard.html"

        self.procs: dict[str, subprocess.Popen] = {}
        self.logs: dict[str, object] = {}

    # ------------------------------------------------------------------
    def _spawn(self, name: str, args: list[str]):
        LOGS.mkdir(parents=True, exist_ok=True)
        handle = open(LOGS / f"{name}.log", "w", encoding="utf-8")
        flags = CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        self.procs[name] = subprocess.Popen(
            [sys.executable, *args],
            cwd=str(ROOT),
            stdout=handle,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
        self.logs[name] = handle

    def start_worker(self, index: int):
        name = f"w{index + 1}"
        port = self.worker_base_port + index
        self._spawn(
            name,
            [
                "worker.py",
                "--id",
                name,
                "--port",
                str(port),
                "--threads",
                str(self.worker_threads),
                "--broker",
                self.broker_url,
            ],
        )
        if not wait_for(f"http://127.0.0.1:{port}/health", timeout=20):
            raise RuntimeError(f"el nodo {name} no respondio en :{port}")

    def stop_worker(self, index: int):
        name = f"w{index + 1}"
        url = self.worker_urls[index]
        try:
            http_json(url + "/shutdown", "POST", {}, timeout=2.0)
        except Exception:
            pass
        proc = self.procs.get(name)
        if proc:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            self.procs.pop(name, None)
        handle = self.logs.pop(name, None)
        if handle:
            handle.close()

    # ------------------------------------------------------------------
    def start(self, workers: int | None = None):
        active = workers if workers is not None else self.workers
        self._spawn(
            "broker",
            [
                "broker.py",
                "--port",
                str(self.broker_port),
                "--log",
                str(PRUEBAS / "event_log.jsonl"),
            ],
        )
        if not wait_for(self.broker_url + "/health", timeout=20):
            raise RuntimeError("el broker no respondio")

        for index in range(active):
            self.start_worker(index)

        self._spawn(
            "coordinator",
            [
                "coordinator.py",
                "--port",
                str(self.coordinator_port),
                "--worker-urls",
                ",".join(self.worker_urls[:active]),
                "--worker-threads",
                str(self.worker_threads),
                "--threads",
                str(self.coordinator_threads),
                "--strategy",
                self.strategy,
                "--broker",
                self.broker_url,
            ],
        )
        if not wait_for(self.coordinator_url + "/health", timeout=20):
            raise RuntimeError("el coordinador no respondio")

        self._spawn(
            "dashboard",
            [
                "-m",
                "http.server",
                str(self.dashboard_port),
                "--directory",
                str(ROOT),
            ],
        )
        wait_for(self.dashboard_url, timeout=10)
        return self

    def set_active_workers(self, count: int):
        http_json(
            self.coordinator_url + "/workers",
            "POST",
            {"urls": self.worker_urls[:count], "threads": self.worker_threads},
            timeout=10,
        )

    def reset(self):
        http_json(self.coordinator_url + "/reset", "POST", {}, timeout=10)

    def metrics(self) -> dict:
        return http_json(self.coordinator_url + "/metrics", timeout=10)

    def broker_metrics(self) -> dict:
        return http_json(self.broker_url + "/metrics", timeout=10)

    def status(self) -> dict:
        workers = []
        for index, url in enumerate(self.worker_urls):
            name = f"w{index + 1}"
            if name not in self.procs:
                continue
            try:
                workers.append(http_json(url + "/health", timeout=2))
            except Exception:
                workers.append({"node": "worker", "worker_id": name, "status": "down"})
        return {
            "broker": http_json(self.broker_url + "/health", timeout=5),
            "coordinator": http_json(self.coordinator_url + "/health", timeout=5),
            "workers": workers,
        }

    def stop(self):
        for name in ("dashboard", "coordinator"):
            proc = self.procs.get(name)
            if proc and proc.poll() is None:
                proc.terminate()
        for index in range(len(self.worker_urls)):
            if f"w{index + 1}" in self.procs:
                self.stop_worker(index)
        broker = self.procs.get("broker")
        if broker and broker.poll() is None:
            broker.terminate()

        deadline = time.time() + 8
        for name, proc in list(self.procs.items()):
            remaining = max(0.5, deadline - time.time())
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                proc.kill()
        for handle in self.logs.values():
            try:
                handle.close()
            except Exception:
                pass
        self.procs.clear()
        self.logs.clear()
