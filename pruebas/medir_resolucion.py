"""Mide el costo de resolver 'localhost' frente a '127.0.0.1'.

Evidencia del ajuste documentado en el informe: en el equipo de pruebas la
resolucion de 'localhost' anadia ~2 s por peticion. El script levanta un
servidor local efimero y cronometra N peticiones con cada host.

Salida: pruebas/resolucion_localhost.json
"""

from __future__ import annotations

import json
import statistics
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Ping(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def medir(host: str, puerto: int, repeticiones: int = 5) -> list[float]:
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        with urllib.request.urlopen(f"http://{host}:{puerto}/", timeout=10) as respuesta:
            respuesta.read()
        tiempos.append(round((time.perf_counter() - inicio) * 1000.0, 2))
    return tiempos


def main():
    servidor = ThreadingHTTPServer(("127.0.0.1", 8123), Ping)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    time.sleep(0.3)

    try:
        localhost = medir("localhost", 8123)
        loopback = medir("127.0.0.1", 8123)
    finally:
        servidor.shutdown()

    resultado = {
        "descripcion": "Costo por peticion HTTP segun el host usado (5 repeticiones)",
        "localhost_ms": localhost,
        "loopback_ms": loopback,
        "promedio_localhost_ms": round(statistics.mean(localhost), 2),
        "promedio_loopback_ms": round(statistics.mean(loopback), 2),
        "mejora_veces": round(statistics.mean(localhost) / statistics.mean(loopback), 1),
    }

    destino = Path(__file__).resolve().parent.parent / "pruebas" / "resolucion_localhost.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
