import os
import sys
import urllib.request
import zlib

BASE = os.path.dirname(os.path.abspath(__file__))
SERVER = "https://www.plantuml.com/plantuml"


def _encode6bit(value: int) -> str:
    value &= 0x3F
    if value < 10:
        return chr(ord("0") + value)
    value -= 10
    if value < 26:
        return chr(ord("A") + value)
    value -= 26
    if value < 26:
        return chr(ord("a") + value)
    value -= 26
    if value == 0:
        return "-"
    if value == 1:
        return "_"
    return "?"


def _encode64(data: bytes) -> str:
    out = []
    for index in range(0, len(data), 3):
        b1 = data[index]
        b2 = data[index + 1] if index + 1 < len(data) else 0
        b3 = data[index + 2] if index + 2 < len(data) else 0
        c1 = b1 >> 2
        c2 = ((b1 & 0x03) << 4) | (b2 >> 4)
        c3 = ((b2 & 0x0F) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        out.append(
            _encode6bit(c1)
            + _encode6bit(c2)
            + _encode6bit(c3)
            + _encode6bit(c4)
        )
    return "".join(out)


def encode(puml: str) -> str:
    raw = zlib.compress(puml.encode("utf-8"))[2:-4]
    return _encode64(raw)


def render(path: str, fmt: str = "png") -> str:
    with open(path, "r", encoding="utf-8") as fh:
        puml = fh.read()
    url = f"{SERVER}/{fmt}/{encode(puml)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    out = os.path.splitext(path)[0] + "." + fmt
    with open(out, "wb") as fh:
        fh.write(data)
    return out


if __name__ == "__main__":
    files = sorted(f for f in os.listdir(BASE) if f.endswith(".puml"))
    for name in files:
        src = os.path.join(BASE, name)
        for fmt in ("png", "svg"):
            try:
                out = render(src, fmt)
                print(
                    f"OK  {fmt.upper():3} {os.path.basename(out):45} "
                    f"{os.path.getsize(out):>8} bytes"
                )
            except Exception as exc:
                print(f"ERR {fmt.upper():3} {name}: {exc}")
                sys.exit(1)
