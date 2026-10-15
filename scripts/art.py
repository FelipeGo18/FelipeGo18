"""Arte del perfil: Real Hasta La Muerte x Chrome Hearts.

Todo el texto se convierte a trazos con fontTools, así que los SVG no dependen de fuentes externas.
Genera assets/hero.svg, assets/notas.svg y assets/tracklist.svg.
"""
import math
import os
import random

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "assets")

BLACK, RED, WHITE, GRAY, DIM, LINE = "#0a0a0a", "#e11d2e", "#f5f5f5", "#a3a3a3", "#6b6b6b", "#262626"
W = 1200


class Font:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def cap(self, size, ch="H"):
        bp = BoundsPen(self.gs)
        self.gs[self.cmap[ord(ch)]].draw(bp)
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

    def d(self, text, size, x, y, tracking=0.0):
        gl, w = self.glyphs(text, size, x, y, tracking)
        return " ".join(g[0] for g in gl if g[0]), w

    def path(self, text, size, x, y, fill, tracking=0.0, extra=""):
        d, w = self.d(text, size, x, y, tracking)
        return f'<path d="{d}" fill="{fill}" {extra}/>', w

    def width(self, text, size, tracking=0.0):
        return self.glyphs(text, size, 0, 0, tracking)[1]


anton = Font(f"{FONTS}/Anton-Regular.ttf")
mono = Font(f"{FONTS}/SpaceMono-Regular.ttf")
monob = Font(f"{FONTS}/SpaceMono-Bold.ttf")
gothic = Font(f"{FONTS}/UnifrakturMaguntia-Book.ttf")


# ---------------------------------------------------------------- materiales

def defs_base(h):
    """Cuero, grano, cromo y el destello que recorre el metal."""
    return f"""<filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/>
  </filter>
  <filter id="leather" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.045 0.06" numOctaves="4" seed="11" result="n"/>
    <feDiffuseLighting in="n" surfaceScale="2.2" lighting-color="#161616" result="l">
      <feDistantLight azimuth="235" elevation="58"/>
    </feDiffuseLighting>
    <feComposite in="l" in2="SourceGraphic" operator="in"/>
  </filter>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-420" y1="0" x2="-180" y2="{h}">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.95"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;{W + 700} 0;{W + 700} 0"
      keyTimes="0;0.4;1" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  {chrome_grad("chromeFrame", 0, h)}"""


def chrome_grad(gid, top, bottom):
    """Plata pulida: bandas claras y oscuras con un horizonte marcado, como joyería."""
    return f"""<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{top:.1f}" x2="0" y2="{bottom:.1f}">
    <stop offset="0" stop-color="#ffffff"/>
    <stop offset="0.28" stop-color="#c9c9c9"/>
    <stop offset="0.48" stop-color="#5c5c5c"/>
    <stop offset="0.52" stop-color="#2b2b2b"/>
    <stop offset="0.56" stop-color="#e6e6e6"/>
    <stop offset="0.8" stop-color="#8f8f8f"/>
    <stop offset="1" stop-color="#f2f2f2"/>
  </linearGradient>"""


def background(h):
    return (f'<rect width="{W}" height="{h}" fill="{BLACK}"/>'
            f'<rect width="{W}" height="{h}" fill="#000" filter="url(#leather)" opacity="0.35"/>')


def overlay(h):
    return f'<rect width="{W}" height="{h}" filter="url(#grain)" pointer-events="none"/>'


def cross_d(cx, cy, size, long_bottom=True):
    """Cruz gótica propia: brazos que se abren y terminan en punta, centro hueco para la gema."""
    r0, w0 = size * 0.10, size * 0.075
    pts = []
    for k, ang in enumerate((0, 90, 180, 270)):
        L = size * (1.45 if (long_bottom and ang == 90) else 1.0)
        w1 = size * 0.2
        local = [(r0, -w0), (L - size * 0.24, -w1), (L - size * 0.12, -w1 + size * 0.05), (L, 0),
                 (L - size * 0.12, w1 - size * 0.05), (L - size * 0.24, w1), (r0, w0)]
        a = math.radians(ang)
        for x, y in local:
            pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def cross(cx, cy, size, gid, gem=True, long_bottom=True):
    d = cross_d(cx, cy, size, long_bottom)
    inner = cross_d(cx, cy, size * 0.8, long_bottom)
    parts = [
        f'<path d="{d}" fill="#000" transform="translate(4 6)" opacity="0.7"/>',
        f'<path d="{d}" fill="url(#{gid})" stroke="#ffffff" stroke-opacity="0.35" stroke-width="1"/>',
        f'<path d="{inner}" fill="none" stroke="#1a1a1a" stroke-opacity="0.55" stroke-width="{max(size * 0.02, 1):.1f}"/>',
        f'<path d="{d}" fill="url(#shine)"/>',
    ]
    if gem:
        r = size * 0.11
        parts += [f'<circle cx="{cx}" cy="{cy}" r="{r * 1.35:.1f}" fill="url(#{gid})" stroke="#000" stroke-opacity="0.5"/>',
                  f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="{RED}"/>',
                  f'<circle cx="{cx - r * 0.35:.1f}" cy="{cy - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#fff" opacity="0.55"/>']
    return "".join(parts)


def frame(h, gid="chromeFrame"):
    """Marco doble de plata con una cruz pequeña en cada esquina."""
    i1, i2 = 22, 30
    out = [f'<rect x="{i1}" y="{i1}" width="{W - 2 * i1}" height="{h - 2 * i1}" fill="none" stroke="url(#{gid})" stroke-width="2"/>',
           f'<rect x="{i2}" y="{i2}" width="{W - 2 * i2}" height="{h - 2 * i2}" fill="none" stroke="#3a3a3a" stroke-width="1"/>']
    for x, y in ((i1, i1), (W - i1, i1), (i1, h - i1), (W - i1, h - i1)):
        out.append(f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" fill="{BLACK}"/>')
        out.append(cross(x, y, 11, gid, gem=False, long_bottom=False))
    return "".join(out)


def chrome_text(font, text, size, x, y, gid, tracking=0.0):
    d, w = font.d(text, size, x, y, tracking)
    return (f'<path d="{d}" fill="#000" transform="translate(3 5)" opacity="0.75"/>'
            f'<path d="{d}" fill="url(#{gid})" stroke="#fff" stroke-opacity="0.3" stroke-width="0.8"/>'
            f'<path d="{d}" fill="url(#shine)"/>'), w


def title(text, y, h_card):
    """Título de sección en gótica cromada con su línea roja debajo."""
    size = 84
    top = y - gothic.cap(size, "T") - 6
    g = chrome_grad("chromeTitle", top, y + 18)
    t, w = chrome_text(gothic, text, size, 70, y, "chromeTitle")
    return g, t, w


def typed(font, text, size, x, y, D, t0, step, t_out, tracking=0.0, fill=None, gid=None):
    """Cada glifo aparece en t0 + i*step y se apaga en t_out (bucle de D segundos)."""
    gl, w = font.glyphs(text, size, x, y, tracking)
    parts = []
    for i, (d, _, _) in enumerate(gl):
        if not d:
            continue
        a = (t0 + i * step) / D
        anim = (f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" '
                f'keyTimes="0;{a:.4f};{t_out / D:.4f}" dur="{D}s" repeatCount="indefinite"/>')
        if gid:
            body = (f'<path d="{d}" fill="#000" transform="translate(3 5)" opacity="0.75"/>'
                    f'<path d="{d}" fill="url(#{gid})" stroke="#fff" stroke-opacity="0.3" stroke-width="0.8"/>'
                    f'<path d="{d}" fill="url(#shine)"/>')
        else:
            body = f'<path d="{d}" fill="{fill}"/>'
        parts.append(f"<g>{anim}{body}</g>")
    return "".join(parts), w, t0 + len(text) * step


def svg_doc(h, label, body, extra_defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{label}">
<defs>
  {defs_base(h)}
  {extra_defs}
</defs>
{background(h)}
{body}
{frame(h)}
{overlay(h)}
</svg>
"""


# ---------------------------------------------------------------- piezas

def brush(x0, y_top, y_bot, width, seed=18):
    """Brochazo rojo RHLM: bordes irregulares, vetas y cerdas sueltas al final."""
    rnd = random.Random(seed)
    bl, br = x0, x0 + width
    top, bot = [], []
    for k in range(61):
        x = bl + (br - bl) * k / 60
        slope = -10 * k / 60
        top.append((x, y_top + slope + rnd.uniform(-5, 5)))
        bot.append((x, y_bot + slope + rnd.uniform(-5, 5)))
    tip = []
    for k in range(9):
        y = y_top + (y_bot - y_top) * k / 8 - 10
        tip += [(br + rnd.uniform(4, 34), y), (br - rnd.uniform(0, 10), y + (y_bot - y_top) / 16)]
    pts = top + tip + bot[::-1] + [(bl - rnd.uniform(6, 14), (y_top + y_bot) / 2)]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    out = [f'<path d="{d}" fill="{RED}"/>']
    for _ in range(26):
        sy, sx = rnd.uniform(y_top + 4, y_bot - 4), rnd.uniform(bl, br - 120)
        out.append(f'<rect x="{sx:.1f}" y="{sy - 10 * (sx - bl) / (br - bl):.1f}" width="{rnd.uniform(60, 260):.1f}" '
                   f'height="{rnd.uniform(1, 2.6):.1f}" fill="#9f1422" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    for _ in range(14):
        out.append(f'<rect x="{br + rnd.uniform(10, 40):.1f}" y="{rnd.uniform(y_top + 6, y_bot - 6) - 10:.1f}" '
                   f'width="{rnd.uniform(20, 90):.1f}" height="{rnd.uniform(1.5, 4):.1f}" fill="{RED}"/>')
    return "".join(out), br + 130


def hero():
    H, D, OUTT = 580, 12, 11.2
    x0 = 76
    s1, s2, s3 = 124, 150, 24
    y1 = 228
    y2 = y1 + 34 + anton.cap(s2)
    y3 = y2 + 64

    g1 = chrome_grad("chromeName", y1 - gothic.cap(s1, "A") - 10, y1 + 24)
    l1, w1, t1 = typed(gothic, "Andrés Felipe", s1, x0, y1, D, 0.3, 0.08, OUTT, tracking=1, gid="chromeName")

    bt, bb = y2 - anton.cap(s2) - 24, y2 + 24
    w2 = anton.width("GONZÁLEZ", s2, 2)
    stroke, br = brush(x0 - 22, bt, bb, w2 + 70)
    bstart, bend = t1 + 0.05, t1 + 0.5
    span = br - x0 + 60
    wipe = (f'<clipPath id="wipe"><rect x="{x0 - 52}" y="{bt - 40}" height="{bb - bt + 80}" width="{span}">'
            f'<animate attributeName="width" values="0;0;{span};{span};0" '
            f'keyTimes="0;{bstart / D:.4f};{bend / D:.4f};{OUTT / D:.4f};1" dur="{D}s" repeatCount="indefinite"/>'
            f'</rect></clipPath>')
    l2, _, t2 = typed(anton, "GONZÁLEZ", s2, x0 + 8, y2, D, bend, 0.08, OUTT, tracking=2, fill=BLACK)
    l3, w3, t3 = typed(monob, "INGENIERO DE SISTEMAS", s3, x0, y3, D, t2 + 0.25, 0.05, OUTT, tracking=3, fill=WHITE)

    ch = monob.cap(s3)
    cursor = (f'<rect x="{x0 + w3 + 10:.1f}" y="{y3 - ch:.1f}" width="14" height="{ch:.1f}" fill="{RED}" opacity="0">'
              f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0;1;0;1;0;1;0;1;0;1;0" '
              f'keyTimes="0;{t3 / D:.4f};{(t3 + .5) / D:.4f};{(t3 + 1) / D:.4f};{(t3 + 1.5) / D:.4f};{(t3 + 2) / D:.4f};'
              f'{(t3 + 2.5) / D:.4f};{(t3 + 3) / D:.4f};{(t3 + 3.5) / D:.4f};{(t3 + 4) / D:.4f};{(t3 + 4.5) / D:.4f};'
              f'{(t3 + 5) / D:.4f};{OUTT / D:.4f}" dur="{D}s" repeatCount="indefinite"/></rect>')

    top_l, _ = mono.path("FG — VOL. 01", 15, x0, 82, DIM, tracking=3)
    tr = "ORGULLOSAMENTE COLOMBIANO"
    top_r, _ = mono.path(tr, 15, W - x0 - mono.width(tr, 15, 3), 82, DIM, tracking=3)

    # cruz cromada con gema roja, flotando
    ccx, ccy, cs = 985, 215, 92
    gc = chrome_grad("chromeCross", ccy - cs, ccy + cs * 1.45)
    float_anim = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" '
                  'dur="5s" repeatCount="indefinite"/>')
    big_cross = f'<g>{float_anim}{cross(ccx, ccy, cs, "chromeCross")}</g>'

    # parental advisory
    pa1, w_pa1 = anton.path("PARENTAL ADVISORY", 22, 0, 0, BLACK, tracking=1)
    pa2, w_pa2 = anton.path("EXPLICIT CODE", 32, 0, 0, WHITE, tracking=1)
    pw, ph = max(w_pa1, w_pa2) + 34, 102
    px, py = W - x0 - pw, H - 76 - ph
    advisory = f"""<g transform="rotate(-4 {px + pw / 2} {py + ph / 2})">
    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{WHITE}"/>
    <g transform="translate({px + (pw - w_pa1) / 2:.1f} {py + 32})">{pa1}</g>
    <rect x="{px + 7}" y="{py + 43}" width="{pw - 14}" height="{ph - 50}" fill="{BLACK}"/>
    <g transform="translate({px + (pw - w_pa2) / 2:.1f} {py + 84})">{pa2}</g>
  </g>"""

    lx, ly, lw = x0, H - 74, 360
    progress = (f'<rect x="{lx}" y="{ly}" width="{lw}" height="3" fill="{LINE}"/>'
                f'<rect x="{lx}" y="{ly}" width="0" height="3" fill="{RED}">'
                f'<animate attributeName="width" values="0;{lw}" dur="{D}s" repeatCount="indefinite"/></rect>'
                f'<circle cx="{lx}" cy="{ly + 1.5}" r="6" fill="{RED}"><animate attributeName="cx" values="{lx};{lx + lw}" '
                f'dur="{D}s" repeatCount="indefinite"/></circle>')
    t_a, _ = mono.path("00:00", 13, lx, ly + 28, DIM, tracking=1)
    rh = "REAL HASTA LA MUERTE"
    t_b, _ = mono.path(rh, 13, lx + lw - mono.width(rh, 13, 1), ly + 28, DIM, tracking=1)

    body = f"""{big_cross}
<g clip-path="url(#wipe)">{stroke}</g>
{l1}
{l2}
{l3}
{cursor}
{top_l}{top_r}
{advisory}
{progress}{t_a}{t_b}"""
    svg = svg_doc(H, "Andrés Felipe González, ingeniero de sistemas", body, extra_defs=g1 + gc + wipe)
    open(os.path.join(OUT, "hero.svg"), "w", encoding="utf-8").write(svg)


NOTAS = [
    "Soy ingeniero de sistemas y construyo soluciones de punta a punta: el backend, la infraestructura "
    "y la interfaz que termina usando la gente. Mi trabajo es que sistemas que no se conocen terminen "
    "hablando el mismo idioma.",
    "Lo que más disfruto es sacar el software de la pantalla. Trabajo con Raspberry Pi, Arduino e IoT, "
    "y si algo se repite, lo automatizo: despliegues, pruebas o un laboratorio remoto completo.",
    "Al diseño le meto el mismo cuidado que al código. Animaciones, detalles y una estética propia, "
    "como la de este perfil.",
]

CREDITOS = [
    ("ROL", "Ingeniero de sistemas"),
    ("BASE", "Colombia"),
    ("ESPECIALIDAD", "Full stack · IoT · Integración"),
    ("EN CURSO", "LaboRemoto · AgroSense"),
    ("SELLO", "Real Hasta La Muerte"),
]


def wrap(text, chars):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + (1 if cur else 0) > chars:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    return lines + [cur]


def notas():
    x0, y_title = 70, 132
    size, lh = 17, 30
    col_w = 660
    chars = int(col_w / (mono.width("x", size)))
    y = 200
    text = []
    for i, p in enumerate(NOTAS):
        for line in wrap(p, chars):
            t, _ = mono.path(line, size, x0, y, "#d4d4d4")
            text.append(t)
            y += lh
        y += 16
    H = max(y + 40, 520)

    cx = x0 + col_w + 60
    cred = [f'<rect x="{cx - 30}" y="176" width="1" height="{H - 236}" fill="{LINE}"/>']
    head, _ = monob.path("CRÉDITOS", 14, cx, 200, RED, tracking=4)
    cred.append(head)
    cy = 248
    for k, v in CREDITOS:
        cred.append(cross(cx + 6, cy - 6, 7, "chromeFrame", gem=False, long_bottom=False))
        a, _ = monob.path(k, 12, cx + 24, cy, DIM, tracking=3)
        b, _ = mono.path(v, 16, cx + 24, cy + 26, WHITE)
        cred += [a, b]
        cy += 66

    g, t, w = title("Liner Notes", y_title, H)
    side, _ = mono.path("SOBRE MÍ", 15, x0 + w + 26, y_title, RED, tracking=3)
    line = f'<rect x="{x0}" y="{y_title + 22}" width="{W - 2 * x0}" height="2" fill="{RED}"/>'
    body = t + side + line + "".join(text) + "".join(cred)
    open(os.path.join(OUT, "notas.svg"), "w", encoding="utf-8").write(
        svg_doc(H, "Liner notes: " + " ".join(NOTAS), body, extra_defs=g))


TRACKS = [
    ("AGROSENSE", "feat. NASA", "Space Apps 2026 con RealE4Life. Rotación de cultivos con datos satelitales.", "PYTHON · FASTAPI · REACT"),
    ("LABOREMOTO", "feat. Raspberry Pi", "Laboratorio remoto para la Universidad Piloto. SSH, VNC e IA.", "RUST · TAURI"),
    ("MICROSERVICIOS", "feat. Kubernetes", "Lo que suena en el trabajo. Keycloak, Kong y NATS.", ".NET · K8S"),
]


def tracklist():
    x0, y_title, top, row = 70, 132, 176, 92
    H = top + row * len(TRACKS) + 64
    g, t, wt = title("Tracklist", y_title, H)
    side, _ = mono.path("LADO A", 15, x0 + wt + 26, y_title, RED, tracking=3)
    rt = f"{len(TRACKS):02d} PISTAS"
    right, _ = mono.path(rt, 15, W - x0 - mono.width(rt, 15, 3), y_title, DIM, tracking=3)
    out = [t, side, right, f'<rect x="{x0}" y="{y_title + 22}" width="{W - 2 * x0}" height="2" fill="{RED}"/>']

    for i, (name, feat, desc, tags) in enumerate(TRACKS):
        y = top + i * row
        num, _ = monob.path(f"{i + 1:02d}", 18, x0, y + 40, RED, tracking=1)
        tname, wn = anton.path(name, 36, x0 + 60, y + 44, WHITE, tracking=1)
        tfeat, _ = mono.path(f"({feat})", 16, x0 + 60 + wn + 14, y + 42, GRAY)
        tdesc, _ = mono.path(desc, 15, x0 + 60, y + 72, DIM)
        ttags, _ = monob.path(tags, 13, W - x0 - monob.width(tags, 13, 2), y + 42, GRAY, tracking=2)
        sep = f'<rect x="{x0}" y="{y + row - 6}" width="{W - 2 * x0}" height="1" fill="{LINE}"/>'
        begin = 0.15 + i * 0.12
        out.append(f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{begin / (begin + 0.35):.3f};1" '
                   f'dur="{begin + 0.35:.2f}s" fill="freeze"/>{num}{tname}{tfeat}{tdesc}{ttags}{sep}</g>')

    ex = x0 + 60 + anton.width(TRACKS[0][0], 36, 1) + 14 + mono.width(f"({TRACKS[0][1]})", 16) + 22
    ey = top + 44
    for j, (vals, dur) in enumerate([("6;22;10;26;6", "0.9s"), ("18;8;24;12;18", "0.7s"), ("10;26;6;20;10", "1.1s")]):
        hs = [int(v) for v in vals.split(";")]
        ys = ";".join(str(ey - h) for h in hs)
        out.append(f'<rect x="{ex + j * 8}" y="{ey - hs[0]}" width="5" height="{hs[0]}" fill="{RED}">'
                   f'<animate attributeName="height" values="{vals}" dur="{dur}" repeatCount="indefinite"/>'
                   f'<animate attributeName="y" values="{ys}" dur="{dur}" repeatCount="indefinite"/></rect>')

    open(os.path.join(OUT, "tracklist.svg"), "w", encoding="utf-8").write(
        svg_doc(H, "Tracklist: " + ", ".join(t[0] for t in TRACKS), "".join(out), extra_defs=g))


if __name__ == "__main__":
    hero()
    notas()
    tracklist()
    print("ok")
