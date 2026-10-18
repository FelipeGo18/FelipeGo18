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
            edge = "max-age=120"  # solo el CDN de Vercel la guarda 2 minutos, para no saturar la API de GitHub
        except Exception as e:  # si GitHub falla, se muestra la última versión que generó la Action
            print("error:", repr(e))
            body = open(os.path.join(ROOT, "assets", "racha.svg"), encoding="utf-8").read()
            edge = "max-age=30"
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        # el navegador y el proxy de imágenes de GitHub nunca guardan copia: siempre piden la versión actual
        self.send_header("Cache-Control", "no-cache, no-store, max-age=0, must-revalidate")
        self.send_header("Vercel-CDN-Cache-Control", edge)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))
