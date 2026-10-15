"""Pasa la dona de lenguajes del 3D (colores de GitHub) a la paleta del perfil."""
import json
import os
import re
import urllib.request

USER = os.environ.get("PROFILE_USER", "FelipeGo18")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "profile-3d-contrib", "profile-rhlm.svg")
PALETA = ["#e11d2e", "#f5f5f5", "#7f1520", "#a3a3a3", "#4a0d12", "#6b6b6b", "#b91c2b", "#d4d4d4"]

query = """query($l:String!){user(login:$l){contributionsCollection{commitContributionsByRepository(maxRepositories:100){
  contributions{totalCount} repository{primaryLanguage{color}}}}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"l": USER}}).encode(),
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    repos = json.load(r)["data"]["user"]["contributionsCollection"]["commitContributionsByRepository"]

peso = {}
for item in repos:
    lang = item["repository"]["primaryLanguage"]
    if lang and lang["color"]:
        c = lang["color"].lower()
        peso[c] = peso.get(c, 0) + item["contributions"]["totalCount"]

svg = open(SVG, encoding="utf-8").read()
for i, color in enumerate(sorted(peso, key=peso.get, reverse=True)):
    svg = re.sub(re.escape(color), PALETA[i % len(PALETA)], svg, flags=re.IGNORECASE)
open(SVG, "w", encoding="utf-8").write(svg)
print("recoloreados:", len(peso))
