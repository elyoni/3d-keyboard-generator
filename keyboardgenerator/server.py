"""
Combined static file + API server.

Serves ui/ as static files on port 8765 and handles:
  POST /api/generate  { kle, split, switchType, borderSize }
    → 200 application/zip   (plate.scad, pcb.scad, bottom.scad)
    → 500 application/json  { error: "…" }
"""

import io
import json
import sys
import tempfile
import zipfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import pykle_serial as kle_serial

from keyboardgenerator.keyboard import Keyboard

PORT = 8765
UI_DIR = Path(__file__).parent.parent / "ui"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    # ── CORS pre-flight ──────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self._cors(200)
        self.end_headers()

    # ── API ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        if self.path == "/api/generate":
            self._handle_generate()
        else:
            self.send_error(404)

    def _handle_generate(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            kle_json = body["kle"]
            split = bool(body.get("split", False))
            switch_type = body.get("switchType", "cherrymx") or "cherrymx"
            border_size = int(body.get("borderSize", 0) or 0)

            rows = json.loads(kle_json)
            kle_obj = kle_serial.deserialize(rows)
            kle_obj.meta.switchType = switch_type
            kle_obj.meta.notes = str(border_size) if border_size else ""
            if split:
                kle_obj.meta.split = True

            zip_bytes = _generate_zip(kle_obj, split)

            self._cors(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="keyboard.zip"')
            self.send_header("Content-Length", str(len(zip_bytes)))
            self.end_headers()
            self.wfile.write(zip_bytes)

        except Exception as exc:
            payload = json.dumps({"error": str(exc)}).encode()
            self._cors(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _cors(self, code: int):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        # Suppress per-request noise; only print errors.
        if int(args[1]) >= 400:
            super().log_message(fmt, *args)


# ── generation helpers ───────────────────────────────────────────────────────


def _generate_zip(kle_obj: kle_serial.Keyboard, split: bool) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)

            kb = Keyboard.from_kle_obj(kle_obj)
            kb.draw_plate().save_as_scad(tmp / "plate.scad")
            kb.draw_pcb().save_as_scad(tmp / "pcb.scad")
            kb.draw_bottom().save_as_scad(tmp / "bottom.scad")

            for f in ("plate.scad", "pcb.scad", "bottom.scad"):
                zf.write(tmp / f, f)

    return buf.getvalue()


# ── entry point ──────────────────────────────────────────────────────────────


def main():
    print(f"Serving UI at http://localhost:{PORT}", flush=True)
    HTTPServer(("", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
