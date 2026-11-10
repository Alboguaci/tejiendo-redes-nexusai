"""Nodos 3, 4 y 5: Worker Nodes con ThreadPool (patron Bulkhead).

Cada nodo es un proceso independiente. Recibe pasos de la Saga por HTTP,
los ejecuta en un pool de hilos propio y publica eventos en el Broker.
"""

from __future__ import annotations

import argparse
import queue
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from common import JsonHandler, http_json, make_server, now_ms, percentile

STEP_LATENCY = {
    "triage": 0.08,
    "rag": 0.18,
    "compliance": 0.12,
    "compensate": 0.05,
}


class WorkerError(RuntimeError):
    """Fallo de ejecucion. ``kind`` distingue negocio de infraestructura."""

    def __init__(self, message: str, kind: str = "node"):
        super().__init__(message)
        self.kind = kind


class WorkerState:
    def __init__(self, worker_id: str, port: int, threads: int, broker_url: str):
        self.worker_id = worker_id
        self.port = port
        self.threads = threads
        self.broker_url = broker_url.rstrip("/")
        self.pool = ThreadPoolExecutor(max_workers=threads, thread_name_prefix=f"{worker_id}-w")
        self.lock = threading.Lock()
        self.active = 0
        self.completed = 0
        self.errors = 0
        self.latencies = []
        self.chaos_latency_ms = 0
        self.fail_rate = 0.0
        self.started_at = time.time()
        self.event_queue = queue.Queue()
        threading.Thread(target=self._publisher_loop, daemon=True).start()

    def _publisher_loop(self):
        while True:
            event = self.event_queue.get()
            try:
                http_json(
                    self.broker_url + "/publish",
                    "POST",
                    {"topic": "events", "message": event},
                    timeout=2.0,
                )
            except Exception:
                pass

    def publish_event(self, event: str, data: dict):
        payload = {"event": event, "worker": self.worker_id, "ts": now_ms(), **data}
        self.event_queue.put(payload)

    def inc_active(self):
        with self.lock:
            self.active += 1

    def dec_active(self):
        with self.lock:
            self.active = max(0, self.active - 1)

    def record_success(self, latency_s: float):
        with self.lock:
            self.completed += 1
            self.latencies.append(latency_s * 1000.0)
            if len(self.latencies) > 2000:
                self.latencies = self.latencies[-2000:]

    def record_error(self):
        with self.lock:
            self.errors += 1

    def process_task(self, task: dict) -> dict:
        step = task.get("step", "unknown")
        base = STEP_LATENCY.get(step, 0.10)
        latency = base + random.uniform(0.0, 0.03) + (self.chaos_latency_ms / 1000.0)
        time.sleep(latency)

        payload = task.get("payload", {}) or {}
        if step == "compliance" and payload.get("force_fail"):
            raise WorkerError("guardrail: confianza semantica < 0.90", kind="business")
        if step != "compensate" and random.random() < self.fail_rate:
            raise WorkerError("chaos: fallo inyectado en el nodo", kind="node")

        return {
            "status": "ok",
            "worker": self.worker_id,
            "step": step,
            "task_id": task.get("task_id"),
            "latency_ms": round(latency * 1000.0, 2),
            "output": f"{step}:ok",
        }

    def metrics(self):
        with self.lock:
            latencies = list(self.latencies)
            active = self.active
            completed = self.completed
            errors = self.errors
        return {
            "node": "worker",
            "worker_id": self.worker_id,
            "port": self.port,
            "threads": self.threads,
            "active": active,
            "completed": completed,
            "errors": errors,
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
            "p95_latency_ms": round(percentile(latencies, 95), 2),
            "event_queue_depth": self.event_queue.qsize(),
            "chaos_latency_ms": self.chaos_latency_ms,
            "fail_rate": self.fail_rate,
            "uptime_s": round(time.time() - self.started_at, 2),
        }


class WorkerHandler(JsonHandler):
    state: WorkerState

    def handle_get(self):
        path, _ = self._query()
        if path == "/health":
            self._send(200, {"status": "ok", "node": "worker", "worker_id": self.state.worker_id})
        elif path == "/metrics":
            self._send(200, self.state.metrics())
        else:
            self._send(404, {"error": "not found"})

    def handle_post(self):
        path, _ = self._query()
        if path == "/execute":
            task = self._read_json()
            self.state.inc_active()
            start = time.perf_counter()
            try:
                future = self.state.pool.submit(self.state.process_task, task)
                result = future.result(timeout=30)
                elapsed = time.perf_counter() - start
                self.state.record_success(elapsed)
                self.state.publish_event(
                    "task.completed",
                    {
                        "task_id": task.get("task_id"),
                        "step": task.get("step"),
                        "latency_ms": round(elapsed * 1000.0, 2),
                    },
                )
                self._send(200, result)
            except WorkerError as exc:
                elapsed = time.perf_counter() - start
                self.state.record_error()
                self.state.publish_event(
                    "task.failed",
                    {
                        "task_id": task.get("task_id"),
                        "step": task.get("step"),
                        "reason": str(exc),
                        "latency_ms": round(elapsed * 1000.0, 2),
                    },
                )
                self._send(
                    500,
                    {
                        "status": "error",
                        "kind": exc.kind,
                        "worker": self.state.worker_id,
                        "step": task.get("step"),
                        "reason": str(exc),
                    },
                )
            except Exception as exc:  # pragma: no cover - defensivo
                self.state.record_error()
                self._send(500, {"status": "error", "reason": str(exc)})
            finally:
                self.state.dec_active()
        elif path == "/chaos":
            body = self._read_json()
            if "latency_ms" in body:
                self.state.chaos_latency_ms = int(body["latency_ms"])
            if "fail_rate" in body:
                self.state.fail_rate = float(body["fail_rate"])
            self._send(
                200,
                {
                    "ok": True,
                    "chaos_latency_ms": self.state.chaos_latency_ms,
                    "fail_rate": self.state.fail_rate,
                },
            )
        elif path == "/shutdown":
            self._send(200, {"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self._send(404, {"error": "not found"})


def main():
    parser = argparse.ArgumentParser(description="NexusAI Worker Node")
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--broker", default="http://127.0.0.1:8090")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    WorkerHandler.state = WorkerState(args.id, args.port, args.threads, args.broker)
    server = make_server(args.port, WorkerHandler, args.verbose)
    print(
        f"[{args.id}] escuchando en http://127.0.0.1:{args.port} "
        f"con {args.threads} hilos",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        WorkerHandler.state.pool.shutdown(wait=False, cancel_futures=True)
        print(f"[{args.id}] detenido", flush=True)


if __name__ == "__main__":
    main()
