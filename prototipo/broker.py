"""Nodo 2: Message Broker (patron Broker / event bus).

Expone topics en memoria y un log JSONL inmutable para auditoria.
Cada topic es una cola thread-safe; el servidor HTTP es multi-hilo.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import threading
import time
from collections import defaultdict

from common import JsonHandler, make_server, now_ms


class BrokerState:
    MAX_QUEUE = 10000

    def __init__(self, log_path: str):
        self.queues = defaultdict(lambda: queue.Queue(maxsize=self.MAX_QUEUE))
        self.stats = defaultdict(lambda: {"published": 0, "consumed": 0})
        self.dropped = 0
        self.lock = threading.Lock()
        self.log_path = log_path
        self.log_lock = threading.Lock()
        self.started_at = time.time()
        # Consumidor de auditoria: suscriptor real del topic de eventos.
        self.audit_events = 0
        self.audit_by_type = defaultdict(int)
        self.audit_last_ts = 0
        self.stopping = threading.Event()
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    def publish(self, topic: str, message: dict):
        with self.lock:
            target = self.queues[topic]
            try:
                target.put_nowait(message)
            except queue.Full:
                # backpressure controlada: se descarta el evento mas antiguo
                try:
                    target.get_nowait()
                    self.dropped += 1
                except queue.Empty:
                    pass
                target.put_nowait(message)
            self.stats[topic]["published"] += 1
        record = {"ts": now_ms(), "topic": topic, "message": message}
        with self.log_lock:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def consume(self, topic: str, timeout: float):
        try:
            message = self.queues[topic].get(timeout=timeout)
        except queue.Empty:
            return None
        with self.lock:
            self.stats[topic]["consumed"] += 1
        return message

    def start_audit_consumer(self, topic: str = "events"):
        """Suscriptor que drena el topic y construye un indice por tipo de evento."""

        def loop():
            while not self.stopping.is_set():
                message = self.consume(topic, timeout=0.5)
                if message is None:
                    continue
                with self.lock:
                    self.audit_events += 1
                    self.audit_by_type[message.get("event", "desconocido")] += 1
                    self.audit_last_ts = int(message.get("ts") or now_ms())

        threading.Thread(target=loop, name="audit-consumer", daemon=True).start()

    def metrics(self):
        with self.lock:
            topics = {}
            for topic, q in self.queues.items():
                topics[topic] = {
                    "queue_depth": q.qsize(),
                    **self.stats[topic],
                }
            total_published = sum(v["published"] for v in self.stats.values())
            total_consumed = sum(v["consumed"] for v in self.stats.values())
            audit = {
                "events": self.audit_events,
                "types": dict(self.audit_by_type),
                "last_event_ts": self.audit_last_ts,
            }
        return {
            "node": "broker",
            "uptime_s": round(time.time() - self.started_at, 2),
            "topics": topics,
            "total_published": total_published,
            "total_consumed": total_consumed,
            "dropped": self.dropped,
            "audit": audit,
        }


class BrokerHandler(JsonHandler):
    state: BrokerState

    def handle_get(self):
        path, query = self._query()
        if path == "/health":
            self._send(200, {"status": "ok", "node": "broker"})
        elif path == "/metrics":
            self._send(200, self.state.metrics())
        elif path == "/consume":
            topic = query.get("topic", "events")
            timeout = float(query.get("timeout", "5"))
            message = self.state.consume(topic, timeout)
            if message is None:
                self._send(204)
            else:
                self._send(200, message)
        else:
            self._send(404, {"error": "not found"})

    def handle_post(self):
        path, _ = self._query()
        if path == "/publish":
            body = self._read_json()
            topic = body.get("topic", "events")
            message = body.get("message", {})
            self.state.publish(topic, message)
            self._send(200, {"ok": True, "topic": topic})
        elif path == "/shutdown":
            self._send(200, {"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self._send(404, {"error": "not found"})


def main():
    parser = argparse.ArgumentParser(description="NexusAI Message Broker")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--log", default="pruebas/event_log.jsonl")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    BrokerHandler.state = BrokerState(args.log)
    BrokerHandler.state.start_audit_consumer("events")
    server = make_server(args.port, BrokerHandler, args.verbose)
    print(f"[broker] escuchando en http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        BrokerHandler.state.stopping.set()
        server.server_close()
        print("[broker] detenido", flush=True)


if __name__ == "__main__":
    main()
