"""Nodo 1: API Gateway + Saga Orchestrator + Load Balancer.

Concentra tres responsabilidades deliberadamente separadas en clases:

* ``WorkerPool``      -> balanceo (patron Strategy) + Circuit Breaker + Retry.
* ``SagaOrchestrator`` -> maquina de estados triage -> rag -> compliance
                          con compensacion inversa ante fallo.
* ``CoordinatorState`` -> metricas, registro de sagas y servidor HTTP.

El coordinador NO ejecuta el trabajo cognitivo: solo orquesta nodos remotos.
"""

from __future__ import annotations

import argparse
import itertools
import os
import queue
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

from common import JsonHandler, http_json, http_json_status, make_server, now_ms, percentile

SAGA_STEPS = ("triage", "rag", "compliance")


# --------------------------------------------------------------------------
# Errores de dominio
# --------------------------------------------------------------------------
class SagaError(RuntimeError):
    """Fallo controlado durante la ejecucion de un paso de la Saga."""

    def __init__(self, step: str, reason: str, worker: str | None = None, kind: str = "node"):
        super().__init__(reason)
        self.step = step
        self.reason = reason
        self.worker = worker
        self.kind = kind  # node | business | unavailable


# --------------------------------------------------------------------------
# Circuit Breaker (Martin Fowler / Nygard - Release It!)
# --------------------------------------------------------------------------
class CircuitBreaker:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 3, cooldown_s: float = 5.0):
        self.failure_threshold = failure_threshold
        self.cooldown_s = cooldown_s
        self.failures = 0
        self.opened_at = 0.0
        self.state = self.CLOSED
        self.lock = threading.Lock()

    def allow(self) -> bool:
        with self.lock:
            if self.state == self.OPEN:
                if time.time() - self.opened_at >= self.cooldown_s:
                    self.state = self.HALF_OPEN
                    return True
                return False
            return True

    def record_success(self):
        with self.lock:
            self.failures = 0
            self.state = self.CLOSED

    def record_failure(self):
        with self.lock:
            self.failures += 1
            if self.state == self.HALF_OPEN or self.failures >= self.failure_threshold:
                self.state = self.OPEN
                self.opened_at = time.time()


# --------------------------------------------------------------------------
# Patron Strategy para el balanceo de carga
# --------------------------------------------------------------------------
class RoundRobinStrategy:
    name = "round-robin"

    def __init__(self):
        self._counter = itertools.count()
        self._lock = threading.Lock()

    def pick(self, workers):
        if not workers:
            return None
        with self._lock:
            index = next(self._counter)
        return workers[index % len(workers)]


class LeastConnectionsStrategy:
    name = "least-connections"

    def pick(self, workers):
        if not workers:
            return None
        return min(workers, key=lambda w: (w.inflight, w.dispatched))


STRATEGIES = {
    "round-robin": RoundRobinStrategy,
    "least-connections": LeastConnectionsStrategy,
}


class WorkerHandle:
    def __init__(self, worker_id: str, url: str, threads: int):
        self.id = worker_id
        self.url = url.rstrip("/")
        self.threads = threads
        self.breaker = CircuitBreaker()
        self.inflight = 0
        self.dispatched = 0
        self.successes = 0
        self.failures = 0


class WorkerPool:
    """Despacha pasos a los nodos de computo con reintento y aislamiento."""

    def __init__(self, strategy: str = "round-robin", max_attempts: int = 2, call_timeout: float = 10.0):
        self.lock = threading.Lock()
        self.workers: list[WorkerHandle] = []
        self.strategy = STRATEGIES.get(strategy, RoundRobinStrategy)()
        self.max_attempts = max(1, max_attempts)
        self.call_timeout = call_timeout

    def set_workers(self, specs):
        """specs: lista de dicts con id, url, threads."""
        with self.lock:
            existing = {w.id: w for w in self.workers}
            rebuilt = []
            for spec in specs:
                handle = existing.get(spec["id"]) or WorkerHandle(
                    spec["id"], spec["url"], int(spec.get("threads", 0))
                )
                handle.url = spec["url"].rstrip("/")
                handle.threads = int(spec.get("threads", handle.threads))
                rebuilt.append(handle)
            self.workers = rebuilt

    def snapshot(self):
        with self.lock:
            return [
                {
                    "id": w.id,
                    "url": w.url,
                    "threads": w.threads,
                    "breaker": w.breaker.state,
                    "consecutive_failures": w.breaker.failures,
                    "inflight": w.inflight,
                    "dispatched": w.dispatched,
                    "successes": w.successes,
                    "failures": w.failures,
                }
                for w in self.workers
            ]

    def reset_breakers(self):
        with self.lock:
            for worker in self.workers:
                worker.breaker.record_success()

    def execute(self, step: str, task: dict, preferred: str | None = None) -> dict:
        tried: set[str] = set()
        last_error: str | None = None
        last_kind = "node"

        for attempt in range(self.max_attempts):
            with self.lock:
                candidates = [
                    w for w in self.workers if w.id not in tried and w.breaker.allow()
                ]
            if not candidates:
                break

            worker = None
            if preferred and attempt == 0:
                worker = next((w for w in candidates if w.id == preferred), None)
            worker = worker or self.strategy.pick(candidates)

            tried.add(worker.id)
            with self.lock:
                worker.inflight += 1
                worker.dispatched += 1

            start = time.perf_counter()
            status, body = http_json_status(
                worker.url + "/execute", task, timeout=self.call_timeout
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            with self.lock:
                worker.inflight = max(0, worker.inflight - 1)

            body = body if isinstance(body, dict) else {}
            if status == 200 and body.get("status") == "ok":
                worker.breaker.record_success()
                with self.lock:
                    worker.successes += 1
                return {
                    "result": body,
                    "worker": worker.id,
                    "attempt": attempt + 1,
                    "latency_ms": round(elapsed_ms, 2),
                }

            last_error = body.get("reason") or body.get("error") or f"HTTP {status}"
            last_kind = body.get("kind") or "node"

            if last_kind == "business":
                # El nodo respondio correctamente: la regla de negocio fallo.
                # No se castiga al nodo ni se reintenta en otro.
                raise SagaError(step, str(last_error), worker.id, kind="business")

            worker.breaker.record_failure()
            with self.lock:
                worker.failures += 1

        if last_error is None:
            raise SagaError(
                step,
                "sin nodos disponibles (Circuit Breaker abierto en todos los nodos)",
                None,
                kind="unavailable",
            )
        raise SagaError(step, str(last_error), None, kind=last_kind)


# --------------------------------------------------------------------------
# Saga orquestada con compensacion
# --------------------------------------------------------------------------
class SagaOrchestrator:
    def __init__(self, pool: WorkerPool, publish, record_step):
        self.pool = pool
        self.publish = publish
        self.record_step = record_step

    def run(self, task: dict):
        saga_id = str(task.get("task_id") or uuid.uuid4().hex[:10])
        payload = task.get("payload") or {}
        started = time.perf_counter()

        steps: list[dict] = []
        completed: list[dict] = []

        self.publish(
            "saga.started",
            {"saga_id": saga_id, "canal": payload.get("canal", "desconocido")},
        )

        for step in SAGA_STEPS:
            step_task = {"task_id": saga_id, "step": step, "payload": payload}
            try:
                outcome = self.pool.execute(step, step_task)
            except SagaError as exc:
                compensation = self._compensate(saga_id, completed)
                duration = round((time.perf_counter() - started) * 1000.0, 2)
                self.publish(
                    "saga.rolled_back",
                    {
                        "saga_id": saga_id,
                        "failed_step": step,
                        "reason": exc.reason,
                        "compensated_steps": len(compensation),
                        "duration_ms": duration,
                    },
                )
                return 409, {
                    "status": "rolled_back",
                    "saga_id": saga_id,
                    "failed_step": step,
                    "reason": exc.reason,
                    "kind": exc.kind,
                    "steps": steps,
                    "compensation": compensation,
                    "duration_ms": duration,
                }

            steps.append(
                {
                    "step": step,
                    "worker": outcome["worker"],
                    "attempt": outcome["attempt"],
                    "latency_ms": outcome["latency_ms"],
                    "status": "ok",
                }
            )
            self.record_step(step, outcome["latency_ms"])
            completed.append({"step": step, "worker": outcome["worker"]})
            self.publish(
                "saga.step.completed",
                {
                    "saga_id": saga_id,
                    "step": step,
                    "worker": outcome["worker"],
                    "latency_ms": outcome["latency_ms"],
                },
            )

        duration = round((time.perf_counter() - started) * 1000.0, 2)
        self.publish("saga.completed", {"saga_id": saga_id, "duration_ms": duration})
        return 200, {
            "status": "completed",
            "saga_id": saga_id,
            "steps": steps,
            "duration_ms": duration,
        }

    def _compensate(self, saga_id: str, completed: list[dict]) -> list[dict]:
        compensation = []
        for done in reversed(completed):
            comp_task = {
                "task_id": saga_id,
                "step": "compensate",
                "payload": {"compensate_step": done["step"]},
            }
            try:
                outcome = self.pool.execute("compensate", comp_task, preferred=done["worker"])
                compensation.append(
                    {
                        "step": done["step"],
                        "status": "compensated",
                        "worker": outcome["worker"],
                        "latency_ms": outcome["latency_ms"],
                    }
                )
            except SagaError as exc:
                compensation.append(
                    {"step": done["step"], "status": "compensation_failed", "reason": exc.reason}
                )
        return compensation


# --------------------------------------------------------------------------
# Estado y servidor del coordinador
# --------------------------------------------------------------------------
class CoordinatorState:
    def __init__(self, args):
        self.started_at = time.time()
        self.metrics_started_at = time.time()
        self.lock = threading.Lock()

        self.total = 0
        self.completed = 0
        self.rolled_back = 0
        self.rejected = 0
        self.active = 0
        self.latencies: list[float] = []
        self.step_latencies = defaultdict(list)
        self.recent: list[dict] = []

        self.broker_url = args.broker.rstrip("/")
        self.threads = args.threads
        self.task_timeout = args.task_timeout

        self.pool = WorkerPool(
            strategy=args.strategy,
            max_attempts=args.max_attempts,
            call_timeout=args.call_timeout,
        )
        self.pool.set_workers(
            [
                {"id": f"w{index + 1}", "url": url.strip(), "threads": args.worker_threads}
                for index, url in enumerate(args.worker_urls.split(","))
                if url.strip()
            ]
        )

        self.dispatch = ThreadPoolExecutor(
            max_workers=args.threads, thread_name_prefix="dispatch"
        )
        self.saga = SagaOrchestrator(self.pool, self.publish, self.record_step)

        self.event_queue: queue.Queue = queue.Queue()
        threading.Thread(target=self._publisher_loop, daemon=True).start()

    # ----------------------------- eventos ------------------------------
    def publish(self, event: str, data: dict):
        self.event_queue.put({"event": event, "source": "coordinator", "ts": now_ms(), **data})

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

    # ----------------------------- metricas -----------------------------
    def record_step(self, step: str, latency_ms: float):
        with self.lock:
            bucket = self.step_latencies[step]
            bucket.append(latency_ms)
            if len(bucket) > 3000:
                self.step_latencies[step] = bucket[-3000:]

    def submit_task(self, task: dict):
        with self.lock:
            self.active += 1
        start = time.perf_counter()
        try:
            future = self.dispatch.submit(self.saga.run, task)
            status, body = future.result(timeout=self.task_timeout)
        except Exception as exc:
            status, body = 500, {"status": "error", "reason": str(exc)}
        elapsed = (time.perf_counter() - start) * 1000.0

        with self.lock:
            self.active = max(0, self.active - 1)
            self.total += 1
            self.latencies.append(elapsed)
            if len(self.latencies) > 5000:
                self.latencies = self.latencies[-5000:]
            if status == 200:
                self.completed += 1
            elif status == 409:
                self.rolled_back += 1
            else:
                self.rejected += 1
            self.recent.append(
                {
                    "saga_id": body.get("saga_id"),
                    "status": body.get("status"),
                    "http_status": status,
                    "failed_step": body.get("failed_step"),
                    "duration_ms": body.get("duration_ms"),
                    "e2e_latency_ms": round(elapsed, 2),
                    "workers": [s.get("worker") for s in body.get("steps", [])],
                }
            )
            if len(self.recent) > 50:
                self.recent.pop(0)

        body["e2e_latency_ms"] = round(elapsed, 2)
        return status, body

    def reset(self, breakers: bool = True):
        with self.lock:
            self.total = 0
            self.completed = 0
            self.rolled_back = 0
            self.rejected = 0
            self.latencies = []
            self.step_latencies.clear()
            self.recent = []
            self.metrics_started_at = time.time()
        if breakers:
            self.pool.reset_breakers()

    def metrics(self):
        with self.lock:
            latencies = list(self.latencies)
            total = self.total
            completed = self.completed
            rolled_back = self.rolled_back
            rejected = self.rejected
            active = self.active
            steps = {k: list(v) for k, v in self.step_latencies.items()}
            recent = list(self.recent)[-10:]
            window = max(time.time() - self.metrics_started_at, 0.001)

        handled = completed + rolled_back
        return {
            "node": "coordinator",
            "uptime_s": round(time.time() - self.started_at, 2),
            "strategy": self.pool.strategy.name,
            "dispatch_threads": self.threads,
            "total_tasks": total,
            "completed": completed,
            "rolled_back": rolled_back,
            "rejected": rejected,
            "active": active,
            "handled_rate_pct": round(handled / total * 100.0, 2) if total else 0.0,
            "completion_rate_pct": round(completed / total * 100.0, 2) if total else 0.0,
            "throughput_rps": round(handled / window, 2),
            "latency_ms": {
                "avg": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
                "p50": round(percentile(latencies, 50), 2),
                "p95": round(percentile(latencies, 95), 2),
                "p99": round(percentile(latencies, 99), 2),
                "max": round(max(latencies), 2) if latencies else 0.0,
            },
            "steps": {
                name: {
                    "count": len(values),
                    "avg": round(sum(values) / len(values), 2) if values else 0.0,
                    "p95": round(percentile(values, 95), 2),
                }
                for name, values in steps.items()
            },
            "workers": self.pool.snapshot(),
            "recent_sagas": recent,
        }


class CoordinatorHandler(JsonHandler):
    state: CoordinatorState

    def handle_get(self):
        path, _ = self._query()
        if path == "/health":
            self._send(200, {"status": "ok", "node": "coordinator"})
        elif path == "/metrics":
            self._send(200, self.state.metrics())
        elif path == "/workers":
            self._send(200, {"workers": self.state.pool.snapshot()})
        else:
            self._send(404, {"error": "not found"})

    def handle_post(self):
        path, _ = self._query()
        if path == "/task":
            body = self._read_json()
            status, result = self.state.submit_task(body)
            self._send(status, result)
        elif path == "/workers":
            body = self._read_json()
            specs = [
                {"id": f"w{index + 1}", "url": url, "threads": body.get("threads", 0)}
                for index, url in enumerate(body.get("urls", []))
            ]
            self.state.pool.set_workers(specs)
            self._send(200, {"ok": True, "workers": self.state.pool.snapshot()})
        elif path == "/reset":
            body = self._read_json()
            self.state.reset(breakers=body.get("breakers", True))
            self._send(200, {"ok": True, "reset": True, "breakers": body.get("breakers", True)})
        elif path == "/shutdown":
            self._send(200, {"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self._send(404, {"error": "not found"})


def main():
    parser = argparse.ArgumentParser(description="NexusAI API Gateway + Saga Orchestrator")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--worker-urls",
        default="http://127.0.0.1:8101,http://127.0.0.1:8102,http://127.0.0.1:8103",
    )
    parser.add_argument("--worker-threads", type=int, default=4)
    parser.add_argument("--threads", type=int, default=16, help="hilos del pool de despacho")
    parser.add_argument("--broker", default="http://127.0.0.1:8090")
    parser.add_argument("--strategy", choices=list(STRATEGIES), default="round-robin")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--call-timeout", type=float, default=10.0)
    parser.add_argument("--task-timeout", type=float, default=120.0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    CoordinatorHandler.state = CoordinatorState(args)
    server = make_server(args.port, CoordinatorHandler, args.verbose)
    print(
        f"[coordinator] http://127.0.0.1:{args.port} | "
        f"hilos={args.threads} | estrategia={args.strategy} | "
        f"nodos={args.worker_urls}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("[coordinator] detenido", flush=True)


if __name__ == "__main__":
    main()
