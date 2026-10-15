"""Genera hero.svg y tracklist.svg (estética Street / RHLM) con texto convertido a trazos."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "assets")

BLACK, RED, WHITE, GRAY, DIM, LINE = "#0a0a0a", "#e11d2e", "#f5f5f5", "#a3a3a3", "#6b6b6b", "#222222"


class Font:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def cap(self, size):
        bp = BoundsPen(self.gs)
        self.gs[self.cmap[ord("H")]].draw(bp)
        return bp.bounds[3] * size / self.upm

    def glyphs(self, text, size, x, y, tracking=0.0):
        sc = size / self.upm
        out, cx = [], x
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                raise SystemExit(f"glifo faltante: {ch!r}")
            adv = self.hmtx[g][0] * sc
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, y)))
            out.append((pen.getCommands(), cx, adv))
            cx += adv + tracking
        return out, cx - tracking - x

    def path(self, text, size, x, y, fill, tracking=0.0, extra=""):
        gl, w = self.glyphs(text, size, x, y, tracking)
        d = " ".join(g[0] for g in gl if g[0])
        return f'<path d="{d}" fill="{fill}" {extra}/>', w

    def width(self, text, size, tracking=0.0):
        return self.glyphs(text, size, 0, 0, tracking)[1]


anton = Font(f"{FONTS}/Anton-Regular.ttf")
mono = Font(f"{FONTS}/SpaceMono-Regular.ttf")
monob = Font(f"{FONTS}/SpaceMono-Bold.ttf")

GRAIN = """<filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.09 0"/>
  </filter>"""

ROUGH = """<filter id="rough" x="-5%" y="-20%" width="110%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.035 0.6" numOctaves="3" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="26" xChannelSelector="R" yChannelSelector="G"/>
  </filter>"""


def typed(font, text, size, x, y, fill, t0, step, D, t_out, tracking=0.0):
    """Cada glifo aparece en t0 + i*step y desaparece en t_out (bucle de D segundos)."""
    gl, w = font.glyphs(text, size, x, y, tracking)
    parts, i = [], 0
    for d, _, _ in gl:
        if not d:
            i += 1
            continue
        a = (t0 + i * step) / D
        parts.append(
            f'<path d="{d}" fill="{fill}"><animate attributeName="opacity" calcMode="discrete" '
            f'values="0;1;0" keyTimes="0;{a:.4f};{t_out / D:.4f}" dur="{D}s" repeatCount="indefinite"/></path>'
        )
        i += 1
    return "\n".join(parts), w, t0 + len(text) * step


def hero():
    W, H, D, OUTT = 1200, 520, 12, 11.2
    x0 = 64
    s1, s2, s3 = 92, 150, 25
    y1 = 190
    y2 = y1 + 28 + anton.cap(s2)
    y3 = y2 + 66

    l1, w1, t1 = typed(anton, "ANDRÉS FELIPE", s1, x0, y1, WHITE, 0.3, 0.07, D, OUTT, tracking=2)
    bstart, bend = t1 + 0.05, t1 + 0.5
    l2, w2, t2 = typed(anton, "GONZÁLEZ", s2, x0 + 8, y2, BLACK, bend, 0.08, D, OUTT, tracking=2)
    l3, w3, t3 = typed(monob, "INGENIERO DE SISTEMAS", s3, x0, y3, WHITE, t2 + 0.25, 0.05, D, OUTT, tracking=3)

    # brochazo rojo detrás de GONZÁLEZ: bordes irregulares y cerdas sueltas generadas con semilla fija
    import random
    rnd = random.Random(18)
    bt, bb = y2 - anton.cap(s2) - 24, y2 + 24
    bl, br = x0 - 22, x0 + 8 + w2 + 40
    top_pts, bot_pts = [], []
    n = 60
    for k in range(n + 1):
        x = bl + (br - bl) * k / n
        slope = -10 * k / n
        top_pts.append((x, bt + slope + rnd.uniform(-5, 5)))
        bot_pts.append((x, bb + slope + rnd.uniform(-5, 5)))
    # punta derecha deshilachada
    tip = []
    for k in range(9):
        y = bt + (bb - bt) * k / 8 - 10
        tip.append((br + rnd.uniform(4, 34), y))
        tip.append((br - rnd.uniform(0, 10), y + (bb - bt) / 16))
    pts = top_pts + tip + bot_pts[::-1] + [(bl - rnd.uniform(6, 14), (bt + bb) / 2)]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    streaks = []
    for _ in range(26):
        sy = rnd.uniform(bt + 4, bb - 4)
        sx = rnd.uniform(bl, br - 120)
        streaks.append(f'<rect x="{sx:.1f}" y="{sy - 10 * (sx - bl) / (br - bl):.1f}" width="{rnd.uniform(60, 260):.1f}" '
                       f'height="{rnd.uniform(1, 2.6):.1f}" fill="#9f1422" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    bristles = []
    for _ in range(14):
        sy = rnd.uniform(bt + 6, bb - 6) - 10
        sx = br + rnd.uniform(10, 40)
        bristles.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{rnd.uniform(20, 90):.1f}" height="{rnd.uniform(1.5, 4):.1f}" fill="{RED}"/>')
    brush = f'<path d="{d}" fill="{RED}"/>' + "".join(streaks) + "".join(bristles)
    br += 130
    wipe = (f'<clipPath id="wipe"><rect x="{bl - 30}" y="{bt - 40}" height="{bb - bt + 80}" width="{br - bl + 60}">'
            f'<animate attributeName="width" values="0;0;{br - bl + 60};{br - bl + 60};0" '
            f'keyTimes="0;{bstart / D:.4f};{bend / D:.4f};{OUTT / D:.4f};1" dur="{D}s" repeatCount="indefinite"/>'
            f'</rect></clipPath>')

    # cursor que parpadea al final de la línea 3
    cx = x0 + w3 + 10
    ch = monob.cap(s3)
    cursor = (f'<rect x="{cx:.1f}" y="{y3 - ch:.1f}" width="14" height="{ch:.1f}" fill="{RED}">'
              f'<animate attributeName="opacity" values="0;1;0;1;0" keyTimes="0;0.25;0.5;0.75;1" '
              f'dur="1s" repeatCount="indefinite"/></rect>')

    # textos pequeños del "álbum"
    top_l, _ = mono.path("FG18 — VOL. 01", 15, x0, 62, DIM, tracking=2)
    tr = "ORGULLOSAMENTE COLOMBIANO"
    top_r, _ = mono.path(tr, 15, W - 64 - mono.width(tr, 15, 2), 62, DIM, tracking=2)

    # "18" gigante en contorno, al fondo
    big, wbig = anton.path("18", 380, W - 64 - anton.width("18", 380), 400, "none",
                           extra=f'stroke="#191919" stroke-width="2"')

    # etiqueta tipo parental advisory
    pa1, w_pa1 = anton.path("PARENTAL ADVISORY", 26, 0, 0, BLACK, tracking=1)
    pa2, w_pa2 = anton.path("EXPLICIT CODE", 38, 0, 0, WHITE, tracking=1)
    pw, ph = max(w_pa1, w_pa2) + 40, 118
    px, py = W - 72 - pw, H - 70 - ph
    advisory = f"""<g transform="rotate(-4 {px + pw / 2} {py + ph / 2})">
    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{WHITE}"/>
    <g transform="translate({px + (pw - w_pa1) / 2:.1f} {py + 38})">{pa1}</g>
    <rect x="{px + 8}" y="{py + 50}" width="{pw - 16}" height="{ph - 58}" fill="{BLACK}"/>
    <g transform="translate({px + (pw - w_pa2) / 2:.1f} {py + 98})">{pa2}</g>
  </g>"""

    # línea roja de "pista" con punto que avanza, abajo a la izquierda
    lx, ly, lw = x0, H - 52, 360
    progress = (f'<rect x="{lx}" y="{ly}" width="{lw}" height="3" fill="{LINE}"/>'
                f'<rect x="{lx}" y="{ly}" width="0" height="3" fill="{RED}">'
                f'<animate attributeName="width" values="0;{lw}" dur="{D}s" repeatCount="indefinite"/></rect>'
                f'<circle cx="{lx}" cy="{ly + 1.5}" r="6" fill="{RED}"><animate attributeName="cx" values="{lx};{lx + lw}" '
                f'dur="{D}s" repeatCount="indefinite"/></circle>')
    t_a, _ = mono.path("00:00", 13, lx, ly + 28, DIM, tracking=1)
    t_b, _ = mono.path("REAL HASTA LA MUERTE", 13, lx + lw - mono.width("REAL HASTA LA MUERTE", 13, 1), ly + 28, DIM,
                       tracking=1)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Andrés Felipe González, ingeniero de sistemas">
<defs>
  {GRAIN}
  {wipe}
</defs>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
{big}
<g clip-path="url(#wipe)">{brush}</g>
{l1}
{l2}
{l3}
{cursor}
{top_l}
{top_r}
{advisory}
{progress}
{t_a}
{t_b}
<rect width="{W}" height="{H}" filter="url(#grain)" pointer-events="none"/>
</svg>
"""
    open(f"{OUT}/hero.svg", "w", encoding="utf-8").write(svg)


TRACKS = [
    ("AGROSENSE", "feat. NASA", "Space Apps 2026 con RealE4Life. Rotación de cultivos con datos satelitales.", "PYTHON · FASTAPI · REACT"),
    ("LABOREMOTO", "feat. Raspberry Pi", "Laboratorio remoto para la Universidad Piloto. SSH, VNC e IA.", "RUST · TAURI"),
    ("MICROSERVICIOS", "feat. Kubernetes", "Lo que suena en el trabajo. Keycloak, Kong y NATS.", ".NET · K8S"),
]


def tracklist():
    W = 1200
    x0, top = 64, 150
    row = 92
    H = top + row * len(TRACKS) + 70
    title, wt = anton.path("TRACKLIST", 72, x0, 112, WHITE, tracking=2)
    side, _ = mono.path("LADO A", 15, x0 + wt + 24, 112, RED, tracking=3)
    rt = f"{len(TRACKS):02d} PISTAS"
    right, _ = mono.path(rt, 15, W - 64 - mono.width(rt, 15, 3), 112, DIM, tracking=3)

    rows = []
    for i, (name, feat, desc, tags) in enumerate(TRACKS):
        y = top + i * row
        num, _ = monob.path(f"{i + 1:02d}", 18, x0, y + 40, RED, tracking=1)
        tname, wn = anton.path(name, 36, x0 + 60, y + 44, WHITE, tracking=1)
        tfeat, _ = mono.path(f"({feat})", 16, x0 + 60 + wn + 14, y + 42, GRAY)
        tdesc, _ = mono.path(desc, 15, x0 + 60, y + 72, DIM)
        ttags, _ = monob.path(tags, 13, W - 64 - monob.width(tags, 13, 2), y + 42, GRAY, tracking=2)
        sep = f'<rect x="{x0}" y="{y + row - 6}" width="{W - 2 * x0}" height="1" fill="{LINE}"/>'
        begin = 0.15 + i * 0.12
        rows.append(f'<g opacity="1"><animate attributeName="opacity" values="0;0;1" keyTimes="0;{begin / (begin + 0.35):.3f};1" '
                    f'dur="{begin + 0.35:.2f}s" fill="freeze"/>{num}{tname}{tfeat}{tdesc}{ttags}{sep}</g>')

    # ecualizador "sonando ahora" en la pista 01
    ex, ey = x0 + 60 + anton.width("AGROSENSE", 36, 1) + 14 + mono.width("(feat. NASA)", 16) + 22, top + 44
    eq = []
    for j, (vals, dur) in enumerate([("6;22;10;26;6", "0.9s"), ("18;8;24;12;18", "0.7s"), ("10;26;6;20;10", "1.1s")]):
        bx = ex + j * 8
        hs = [int(v) for v in vals.split(";")]
        ys = ";".join(str(ey - h) for h in hs)
        eq.append(f'<rect x="{bx}" y="{ey - hs[0]}" width="5" height="{hs[0]}" fill="{RED}">'
                  f'<animate attributeName="height" values="{vals}" dur="{dur}" repeatCount="indefinite"/>'
                  f'<animate attributeName="y" values="{ys}" dur="{dur}" repeatCount="indefinite"/></rect>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tracklist: proyectos de Felipe">
<defs>{GRAIN}</defs>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
<rect x="{x0}" y="132" width="{W - 2 * x0}" height="2" fill="{RED}"/>
{title}{side}{right}
{''.join(rows)}
{''.join(eq)}
<rect width="{W}" height="{H}" filter="url(#grain)" pointer-events="none"/>
</svg>
"""
    open(f"{OUT}/tracklist.svg", "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    hero()
    tracklist()
    print("ok")
