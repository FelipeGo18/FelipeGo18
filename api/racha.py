"""Racha en vivo: GitHub pide esta imagen cada vez que alguien abre el perfil."""
import os
import sys
from http.server import BaseHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cards  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            body = cards.render(*cards.contributions())
            # el CDN de Vercel la guarda 5 minutos; el proxy de GitHub siempre vuelve a preguntar
            cache = "public, max-age=0, s-maxage=300, stale-while-revalidate=600"
        except Exception as e:  # si GitHub falla, se muestra la última versión que generó la Action
            print("error:", repr(e))
            body = open(os.path.join(ROOT, "assets", "racha.svg"), encoding="utf-8").read()
            cache = "public, max-age=0, s-maxage=60"
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))
