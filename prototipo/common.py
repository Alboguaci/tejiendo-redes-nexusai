"""Utilidades compartidas del prototipo NexusAI 2.0.

Solo usa la biblioteca estándar de Python para que el prototipo sea
reproducible en cualquier equipo sin dependencias externas.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class JsonHandler(BaseHTTPRequestHandler):
    """Handler HTTP mínimo con respuestas JSON."""

    protocol_version = "HTTP/1.1"
    server_version = "NexusAI/2.0"

    def log_message(self, fmt, *args):  # silencia el log por defecto
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    def _send(self, code: int, obj=None):
        body = b"" if obj is None else json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _query(self):
        parsed = urlparse(self.path)
        return parsed.path, {k: v[-1] for k, v in parse_qs(parsed.query).items()}

    def do_GET(self):  # noqa: N802
        try:
            self.handle_get()
        except Exception as exc:  # pragma: no cover - defensivo
            self._send(500, {"error": str(exc)})

    def do_POST(self):  # noqa: N802
        try:
            self.handle_post()
        except Exception as exc:  # pragma: no cover - defensivo
            self._send(500, {"error": str(exc)})

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def handle_get(self):
        self._send(404, {"error": "not found"})

    def handle_post(self):
        self._send(404, {"error": "not found"})


def make_server(port: int, handler, verbose: bool = False) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    server.daemon_threads = True
    server.verbose = verbose
    return server


def http_json(url: str, method: str = "GET", payload=None, timeout: float = 10.0):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def http_json_status(url: str, payload=None, timeout: float = 30.0):
    """Devuelve (status_code, body) incluso ante errores HTTP."""
    try:
        return 200, http_json(url, "POST", payload, timeout)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = {"error": raw.decode("utf-8", errors="replace")}
        return exc.code, body
    except Exception as exc:
        return 0, {"error": str(exc)}


def wait_for(url: str, timeout: float = 20.0, interval: float = 0.2) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            http_json(url, timeout=1.0)
            return True
        except Exception:
            time.sleep(interval)
    return False


def percentile(values, p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    k = (len(ordered) - 1) * (p / 100.0)
    lower = int(k)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (k - lower))


def now_ms() -> float:
    return round(time.time() * 1000.0, 2)
