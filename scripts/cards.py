"""Tarjeta de racha propia: consulta las contribuciones por GraphQL y dibuja assets/racha.svg."""
import datetime as dt
import json
import math
import os
import urllib.request

from art import DIM, GRAY, LINE, OUT, RED, W, anton, chrome_grad, chrome_text, mono, monob, svg_doc, title

USER = os.environ.get("PROFILE_USER", "FelipeGo18")
TOKEN = os.environ["GITHUB_TOKEN"]
TZ = dt.timezone(dt.timedelta(hours=-5))  # Colombia
MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]


def contributions():
    created = gql("query($l:String!){user(login:$l){createdAt}}", l=USER)["user"]["createdAt"]
    first_year = int(created[:4])
    today = dt.datetime.now(TZ).date()
    days = {}
    q = """query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t){
      contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    for year in range(first_year, today.year + 1):
        data = gql(q, l=USER, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z")
        for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[dt.date.fromisoformat(d["date"])] = d["contributionCount"]
    return {k: v for k, v in sorted(days.items()) if k <= today}, today


def streaks(days, today):
    total = sum(days.values())
    longest, run, run_start, best = 0, 0, None, (None, None)
    for d, c in days.items():
        if c > 0:
            if run == 0:
                run_start = d
            run += 1
            if run > longest:
                longest, best = run, (run_start, d)
        else:
            run = 0
    # la racha actual no se rompe si hoy todavía no hay contribuciones
    cur, d = 0, today if days.get(today, 0) > 0 else today - dt.timedelta(days=1)
    cur_end = d
    while days.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)
    cur_start = d + dt.timedelta(days=1)
    return total, (cur, cur_start, cur_end), (longest, *best)


def fecha(d):
    return f"{d.day} {MESES[d.month - 1]} {d.year}" if d else "—"


def card(days, today):
    total, (cur, cs, ce), (lng, ls, le) = streaks(days, today)
    H, x0, y_title = 520, 70, 132
    g, t, wt = title("Racha", y_title, H)
    out = [t]
    live, _ = mono.path("EN VIVO", 15, x0 + wt + 46, y_title, RED, tracking=3)
    dot = (f'<circle cx="{x0 + wt + 30}" cy="{y_title - 6}" r="6" fill="{RED}">'
           f'<animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    upd = f"ACTUALIZADO {fecha(today)}"
    right, _ = mono.path(upd, 15, W - x0 - mono.width(upd, 15, 3), y_title, DIM, tracking=3)
    out += [live, dot, right, f'<rect x="{x0}" y="{y_title + 22}" width="{W - 2 * x0}" height="2" fill="{RED}"/>']

    cols = [
        (f"{total:,}".replace(",", "."), "CONTRIBUCIONES", f"desde {next(iter(days)).year}" if days else "en total", None),
        (str(cur), "RACHA ACTUAL", f"{fecha(cs)} — {fecha(ce)}" if cur else "a empezar otra", RED),
        (str(lng), "RACHA MÁS LARGA", f"{fecha(ls)} — {fecha(le)}" if lng else "—", None),
    ]
    cw = (W - 2 * x0) / 3
    ny = 300
    defs = g + chrome_grad("chromeNum", ny - anton.cap(100) - 4, ny + 6)
    for i, (num, label, sub, color) in enumerate(cols):
        mid = x0 + i * cw + cw / 2
        wn = anton.width(num, 100, 2)
        if color:
            n, _ = anton.path(num, 100, mid - wn / 2, ny, color, tracking=2)
        else:
            n, _ = chrome_text(anton, num, 100, mid - wn / 2, ny, "chromeNum", tracking=2)
        lab, wl = monob.path(label, 14, 0, 0, GRAY, tracking=3)
        sb, ws = mono.path(sub, 12, 0, 0, DIM, tracking=1)
        delay = 0.15 + i * 0.15
        out.append(
            f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{delay / (delay + .4):.3f};1" '
            f'dur="{delay + .4:.2f}s" fill="freeze"/>{n}'
            f'<g transform="translate({mid - wl / 2:.1f} {ny + 34})">{lab}</g>'
            f'<g transform="translate({mid - ws / 2:.1f} {ny + 56})">{sb}</g></g>'
        )
        if i:
            out.append(f'<rect x="{x0 + i * cw:.1f}" y="196" width="1" height="170" fill="{LINE}"/>')

    # forma de onda tipo mixtape con los últimos 365 días
    last = [today - dt.timedelta(days=k) for k in range(364, -1, -1)]
    vals = [days.get(d, 0) for d in last]
    peak = max(vals) or 1
    wy, wh = 432, 30
    step = (W - 2 * x0) / len(vals)
    bars = []
    for k, v in enumerate(vals):
        h = 1.5 + math.sqrt(v / peak) * wh if v else 1.5
        bars.append(f'<rect x="{x0 + k * step:.1f}" y="{wy - h:.1f}" width="{max(step - 1, 1):.1f}" height="{2 * h:.1f}"/>')
    wave = "".join(bars)
    ww = W - 2 * x0
    out.append(f'<g fill="#3a3a3a">{wave}</g>')
    defs += (f'<clipPath id="played"><rect x="{x0}" y="{wy - wh - 4}" height="{2 * wh + 8}" width="{ww}">'
             f'<animate attributeName="width" values="0;{ww};{ww}" keyTimes="0;0.85;1" dur="10s" repeatCount="indefinite"/>'
             f'</rect></clipPath>')
    out.append(f'<g fill="{RED}" clip-path="url(#played)">{wave}</g>')
    for k, d in enumerate(last):
        if d.day == 1:
            m, _ = mono.path(MESES[d.month - 1], 11, x0 + k * step, wy + wh + 24, DIM, tracking=1)
            out.append(m)

    label = f"Racha actual {cur} días, racha más larga {lng} días, {total} contribuciones"
    open(os.path.join(OUT, "racha.svg"), "w", encoding="utf-8").write(svg_doc(H, label, "".join(out), extra_defs=defs))
    print(f"total={total} actual={cur} larga={lng}")


if __name__ == "__main__":
    card(*contributions())
