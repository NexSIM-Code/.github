#!/usr/bin/env python3
"""Planche des logos partenaires du profil : assets/partenaires.svg.

Chaque logo est posé sur une carte blanche, comme dans le carrousel du site
(NexSite-web, src/image/partenaires) : beaucoup de logos ont un texte noir qui
disparaîtrait sur le thème sombre de GitHub. Les images sont intégrées en data
URI, car GitHub n'autorise pas une image SVG à charger des fichiers externes.

Pour ajouter un partenaire : copier son logo depuis NexSite-web dans
assets/partenaires/, l'ajouter à PARTNERS, relancer le script, puis compléter la
liste des noms dans profile/README.md.

Usage : python3 scripts/build_partners.py (macOS : utilise sips pour les PNG)
"""

import base64
import os
import re
import subprocess
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "partenaires")
OUT = os.path.join(ROOT, "assets", "partenaires.svg")

# Ordre d'affichage : fichier → nom affiché (texte alternatif).
PARTNERS = [
    ("Logo-du-Ministere-de-Enseignement-Superieur-et-de-la-Recherche.svg",
     "Ministère de l'Enseignement supérieur et de la Recherche"),
    ("Logo_Bpifrance.svg", "Bpifrance"),
    ("Crédit-Agricole-2020-logo.svg", "Crédit Agricole"),
    ("Logo-Grand-Belfort.png", "Grand Belfort"),
    ("Logo-Aire-Urbaine-Investissement.png", "Aire Urbaine Investissement"),
    ("DECA-BFC.png", "DECA-BFC"),
    ("LOGO-CRUNCHLAB.png", "Crunch Lab (UTBM)"),
    ("logo-scalea.svg", "Scalea"),
    ("logo-consultis-audit.png", "Consultis Audit"),
]

COLS = 3
CARD_W, CARD_H, GAP = 250, 110, 16
PAD_X, PAD_Y = 28, 18


def size(path):
    if path.endswith(".svg"):
        with open(path, encoding="utf-8") as f:
            head = f.read(4000)
        vb = re.search(r'viewBox="([^"]+)"', head)
        _, _, w, h = (float(v) for v in vb.group(1).replace(",", " ").split())
        return w, h
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True, check=True).stdout
    return (float(re.search(r"pixelWidth: (\d+)", out).group(1)),
            float(re.search(r"pixelHeight: (\d+)", out).group(1)))


def main():
    rows = -(-len(PARTNERS) // COLS)
    w = COLS * CARD_W + (COLS - 1) * GAP
    h = rows * CARD_H + (rows - 1) * GAP
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="Partenaires : {escape(", ".join(n for _, n in PARTNERS))}">']
    for i, (file, name) in enumerate(PARTNERS):
        path = os.path.join(SRC, file)
        x = (i % COLS) * (CARD_W + GAP)
        y = (i // COLS) * (CARD_H + GAP)
        iw, ih = size(path)
        scale = min((CARD_W - 2 * PAD_X) / iw, (CARD_H - 2 * PAD_Y) / ih)
        dw, dh = iw * scale, ih * scale
        mime = "image/svg+xml" if file.endswith(".svg") else "image/png"
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{CARD_W - 1}" height="{CARD_H - 1}" '
                   f'rx="10" fill="#FFFFFF" stroke="#D0D7DE"/>')
        out.append(f'<image x="{x + (CARD_W - dw) / 2:.1f}" y="{y + (CARD_H - dh) / 2:.1f}" '
                   f'width="{dw:.1f}" height="{dh:.1f}" href="data:{mime};base64,{data}">'
                   f'<title>{escape(name)}</title></image>')
    out.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{len(PARTNERS)} logos → {os.path.relpath(OUT, ROOT)} ({os.path.getsize(OUT) // 1024} Ko)")


if __name__ == "__main__":
    main()
