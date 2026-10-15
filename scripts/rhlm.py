"""Logo Real Hasta La Muerte animado, a partir del trazo vectorizado en assets/src/rhlm-trace.svg."""
import os
import re

from art import BLACK, OUT, RED, WHITE

src = open(os.path.join(OUT, "src", "rhlm-trace.svg"), encoding="utf-8").read()
paths = "\n".join(re.sub(r'\s*fill="[^"]*"', "", p) for p in re.findall(r"<path [^>]*/>", src))


def logo(c1, c2, name):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 1880 1190" width="560" height="354" role="img" aria-label="Real Hasta La Muerte">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0.35" stop-color="{c1}"/>
    <stop offset="1" stop-color="{c2}"/>
  </linearGradient>
  <clipPath id="reveal">
    <rect x="-40" y="-40" height="1190" width="1880">
      <animate attributeName="width" values="0;1880;1880" keyTimes="0;0.3;1" dur="7s" repeatCount="indefinite"/>
    </rect>
  </clipPath>
</defs>
<g clip-path="url(#reveal)" fill="url(#g)">
{paths}
</g>
</svg>
'''
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    logo(WHITE, RED, "rhlm-dark.svg")
    logo(BLACK, RED, "rhlm-light.svg")
    print("ok")
