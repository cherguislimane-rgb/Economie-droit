#!/usr/bin/env python3
"""
Planche de tickets à découper pour distribuer les codes élèves.

Usage (depuis la racine de mes-copies) :
    python scripts/tickets_codes.py 1STMG
    python scripts/tickets_codes.py TSTMG

Entrée  : codes_prives_<CLASSE>.csv (produit par generate_codes.py) — colonnes nom,prenom,code.
Sortie  : tickets_codes_<CLASSE>.html à la racine → ouvrir dans Chrome/Edge, Ctrl+P,
          « Enregistrer au format PDF » (A4, marges par défaut, « Graphiques d'arrière-plan » coché).
          Page 1 : 32 tickets (4 × 8) à découper. Page 2 : liste de contrôle à cocher.

⚠️ FICHIER PRIVÉ (noms d'élèves) : couvert par le .gitignore (tickets_codes_*.html), jamais publié.
Aucune dépendance : le QR code de l'app est embarqué en dur (URL fixe).
"""

import csv
import html
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL_APP = "https://cherguislimane-rgb.github.io/Economie-droit/"
CLASSES = {
    "1STMG": {"nom": "Première STMG 2", "accent": "#F2A65A"},
    "TSTMG": {"nom": "Terminale STMG 1", "accent": "#E8735A"},
}
RACINE = Path(__file__).resolve().parent.parent

# QR code (version 4, correction M) de URL_APP — grille 33×33, généré une fois pour toutes.
QR_N = 33
QR_PATH = "M0 0h7v1h-7zM12 0h3v1h-3zM16 0h8v1h-8zM26 0h7v1h-7zM0 1h1v1h-1zM6 1h1v1h-1zM11 1h7v1h-7zM21 1h2v1h-2zM26 1h1v1h-1zM32 1h1v1h-1zM0 2h1v1h-1zM2 2h3v1h-3zM6 2h1v1h-1zM8 2h2v1h-2zM11 2h3v1h-3zM15 2h1v1h-1zM17 2h7v1h-7zM26 2h1v1h-1zM28 2h3v1h-3zM32 2h1v1h-1zM0 3h1v1h-1zM2 3h3v1h-3zM6 3h1v1h-1zM8 3h3v1h-3zM14 3h1v1h-1zM16 3h1v1h-1zM19 3h1v1h-1zM24 3h1v1h-1zM26 3h1v1h-1zM28 3h3v1h-3zM32 3h1v1h-1zM0 4h1v1h-1zM2 4h3v1h-3zM6 4h1v1h-1zM8 4h5v1h-5zM15 4h1v1h-1zM18 4h1v1h-1zM21 4h1v1h-1zM23 4h1v1h-1zM26 4h1v1h-1zM28 4h3v1h-3zM32 4h1v1h-1zM0 5h1v1h-1zM6 5h1v1h-1zM8 5h2v1h-2zM11 5h1v1h-1zM14 5h3v1h-3zM20 5h3v1h-3zM26 5h1v1h-1zM32 5h1v1h-1zM0 6h7v1h-7zM8 6h1v1h-1zM10 6h1v1h-1zM12 6h1v1h-1zM14 6h1v1h-1zM16 6h1v1h-1zM18 6h1v1h-1zM20 6h1v1h-1zM22 6h1v1h-1zM24 6h1v1h-1zM26 6h7v1h-7zM8 7h2v1h-2zM11 7h2v1h-2zM15 7h1v1h-1zM19 7h4v1h-4zM24 7h1v1h-1zM0 8h1v1h-1zM2 8h5v1h-5zM9 8h3v1h-3zM13 8h3v1h-3zM17 8h3v1h-3zM22 8h3v1h-3zM26 8h5v1h-5zM0 9h1v1h-1zM4 9h2v1h-2zM7 9h1v1h-1zM12 9h1v1h-1zM16 9h1v1h-1zM18 9h3v1h-3zM23 9h1v1h-1zM26 9h2v1h-2zM29 9h2v1h-2zM32 9h1v1h-1zM2 10h1v1h-1zM6 10h2v1h-2zM10 10h3v1h-3zM15 10h2v1h-2zM18 10h1v1h-1zM20 10h3v1h-3zM24 10h1v1h-1zM28 10h1v1h-1zM30 10h1v1h-1zM1 11h1v1h-1zM5 11h1v1h-1zM8 11h1v1h-1zM11 11h1v1h-1zM14 11h1v1h-1zM16 11h1v1h-1zM21 11h6v1h-6zM28 11h3v1h-3zM32 11h1v1h-1zM1 12h1v1h-1zM3 12h2v1h-2zM6 12h2v1h-2zM9 12h2v1h-2zM15 12h1v1h-1zM18 12h1v1h-1zM22 12h1v1h-1zM24 12h2v1h-2zM27 12h3v1h-3zM0 13h2v1h-2zM3 13h1v1h-1zM10 13h1v1h-1zM12 13h6v1h-6zM19 13h1v1h-1zM23 13h1v1h-1zM26 13h1v1h-1zM29 13h1v1h-1zM31 13h2v1h-2zM2 14h1v1h-1zM4 14h1v1h-1zM6 14h1v1h-1zM8 14h3v1h-3zM21 14h1v1h-1zM25 14h2v1h-2zM31 14h1v1h-1zM0 15h1v1h-1zM2 15h4v1h-4zM7 15h1v1h-1zM9 15h3v1h-3zM13 15h2v1h-2zM16 15h1v1h-1zM20 15h3v1h-3zM25 15h2v1h-2zM29 15h2v1h-2zM2 16h1v1h-1zM5 16h2v1h-2zM8 16h2v1h-2zM12 16h1v1h-1zM14 16h1v1h-1zM17 16h1v1h-1zM22 16h2v1h-2zM25 16h1v1h-1zM27 16h2v1h-2zM32 16h1v1h-1zM0 17h1v1h-1zM2 17h4v1h-4zM9 17h3v1h-3zM13 17h1v1h-1zM16 17h2v1h-2zM19 17h5v1h-5zM26 17h2v1h-2zM29 17h2v1h-2zM32 17h1v1h-1zM0 18h4v1h-4zM5 18h7v1h-7zM13 18h3v1h-3zM17 18h1v1h-1zM20 18h3v1h-3zM25 18h4v1h-4zM30 18h2v1h-2zM2 19h1v1h-1zM5 19h1v1h-1zM7 19h5v1h-5zM13 19h2v1h-2zM16 19h3v1h-3zM20 19h2v1h-2zM25 19h7v1h-7zM0 20h1v1h-1zM2 20h3v1h-3zM6 20h1v1h-1zM8 20h6v1h-6zM16 20h1v1h-1zM19 20h2v1h-2zM22 20h1v1h-1zM24 20h2v1h-2zM27 20h1v1h-1zM29 20h1v1h-1zM31 20h1v1h-1zM0 21h4v1h-4zM5 21h1v1h-1zM8 21h2v1h-2zM12 21h2v1h-2zM15 21h1v1h-1zM18 21h6v1h-6zM26 21h1v1h-1zM32 21h1v1h-1zM0 22h1v1h-1zM3 22h4v1h-4zM9 22h4v1h-4zM14 22h5v1h-5zM20 22h1v1h-1zM28 22h4v1h-4zM0 23h1v1h-1zM2 23h1v1h-1zM4 23h2v1h-2zM9 23h3v1h-3zM14 23h2v1h-2zM18 23h1v1h-1zM21 23h3v1h-3zM25 23h2v1h-2zM28 23h3v1h-3zM0 24h1v1h-1zM2 24h1v1h-1zM6 24h2v1h-2zM11 24h2v1h-2zM14 24h2v1h-2zM17 24h1v1h-1zM19 24h1v1h-1zM22 24h7v1h-7zM31 24h1v1h-1zM8 25h1v1h-1zM10 25h5v1h-5zM18 25h4v1h-4zM24 25h1v1h-1zM28 25h1v1h-1zM30 25h3v1h-3zM0 26h7v1h-7zM11 26h1v1h-1zM13 26h1v1h-1zM15 26h1v1h-1zM18 26h1v1h-1zM20 26h1v1h-1zM23 26h2v1h-2zM26 26h1v1h-1zM28 26h1v1h-1zM30 26h2v1h-2zM0 27h1v1h-1zM6 27h1v1h-1zM8 27h1v1h-1zM10 27h1v1h-1zM21 27h1v1h-1zM23 27h2v1h-2zM28 27h3v1h-3zM0 28h1v1h-1zM2 28h3v1h-3zM6 28h1v1h-1zM8 28h2v1h-2zM11 28h1v1h-1zM13 28h1v1h-1zM15 28h1v1h-1zM18 28h2v1h-2zM22 28h1v1h-1zM24 28h6v1h-6zM32 28h1v1h-1zM0 29h1v1h-1zM2 29h3v1h-3zM6 29h1v1h-1zM8 29h1v1h-1zM11 29h1v1h-1zM13 29h4v1h-4zM19 29h2v1h-2zM24 29h2v1h-2zM28 29h2v1h-2zM31 29h2v1h-2zM0 30h1v1h-1zM2 30h3v1h-3zM6 30h1v1h-1zM8 30h2v1h-2zM11 30h2v1h-2zM14 30h1v1h-1zM17 30h1v1h-1zM20 30h3v1h-3zM26 30h2v1h-2zM29 30h1v1h-1zM0 31h1v1h-1zM6 31h1v1h-1zM9 31h2v1h-2zM12 31h2v1h-2zM16 31h1v1h-1zM19 31h3v1h-3zM25 31h2v1h-2zM28 31h1v1h-1zM30 31h1v1h-1zM0 32h7v1h-7zM8 32h5v1h-5zM14 32h1v1h-1zM17 32h1v1h-1zM19 32h1v1h-1zM22 32h3v1h-3zM26 32h2v1h-2zM31 32h1v1h-1z"


def lire_codes(csv_path: Path) -> list[tuple[str, str, str]]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        extrait = f.read(2048)
        f.seek(0)
        delim = ";" if extrait.count(";") > extrait.count(",") else ","
        lecteur = csv.DictReader(f, delimiter=delim)
        lecteur.fieldnames = [(c or "").strip().lower() for c in (lecteur.fieldnames or [])]
        for col in ("nom", "prenom", "code"):
            if col not in lecteur.fieldnames:
                sys.exit(f"❌ Colonne « {col} » absente de {csv_path} (colonnes : {lecteur.fieldnames})")
        lignes = [
            ((r["nom"] or "").strip(), (r["prenom"] or "").strip(), (r["code"] or "").strip())
            for r in lecteur
        ]
    lignes = [l for l in lignes if any(l)]
    return sorted(lignes, key=lambda l: (l[0].lower(), l[1].lower()))


def svg_qr(taille_mm: float) -> str:
    return (
        f'<svg class="qr" viewBox="0 0 {QR_N} {QR_N}" width="{taille_mm}mm" height="{taille_mm}mm" '
        f'shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg"><path d="{QR_PATH}"/></svg>'
    )


def ticket(nom: str, prenom: str, code: str, classe: dict) -> str:
    e = html.escape
    return f"""<td class="t">
  <div class="bar"></div>
  <table class="int"><tr>
    <td class="txt">
      <div class="classe">{e(classe["nom"])} · Éco-Droit</div>
      <div class="nom">{e(nom)}</div>
      <div class="prenom">{e(prenom)}</div>
      <div class="code">{e(code)}</div>
      <div class="aide">Ton code personnel, à saisir dans l'app.<br>Il ne s'affiche nulle part ailleurs : garde-le.</div>
    </td>
    <td class="qrbox">{svg_qr(15)}<div class="url">cherguislimane-rgb.github.io/<br>Economie-droit</div></td>
  </tr></table>
</td>"""


def page_tickets(lignes, classe: dict) -> str:
    cellules = [ticket(n, p, c, classe) for n, p, c in lignes]
    # complète la dernière ligne avec des cases vides pour garder la grille 4 colonnes
    while len(cellules) % 4:
        cellules.append('<td class="t vide"></td>')
    rangees = ["<tr>" + "".join(cellules[i : i + 4]) + "</tr>" for i in range(0, len(cellules), 4)]
    pages = [rangees[i : i + 8] for i in range(0, len(rangees), 8)]
    return "".join(f'<table class="grille">{"".join(p)}</table>' for p in pages)


def page_controle(lignes, classe: dict) -> str:
    e = html.escape
    lignes_html = "".join(
        f"<tr><td>{i}</td><td>{e(n)}</td><td>{e(p)}</td><td class='mono'>{e(c)}</td><td class='case'></td><td class='case'></td></tr>"
        for i, (n, p, c) in enumerate(lignes, 1)
    )
    return f"""<section class="controle">
  <h1>{e(classe["nom"])} — codes personnels ({len(lignes)} élèves)</h1>
  <p class="rappel">Feuille privée : à garder dans le classeur, jamais à photocopier pour les élèves.
  Cocher « remis » à la distribution du ticket, « testé » quand l'élève a ouvert l'app avec son code.</p>
  <table class="liste">
    <thead><tr><th>#</th><th>Nom</th><th>Prénom</th><th>Code</th><th>remis</th><th>testé</th></tr></thead>
    <tbody>{lignes_html}</tbody>
  </table>
</section>"""


def generer(cle: str) -> Path:
    if cle not in CLASSES:
        sys.exit("Usage : python scripts/tickets_codes.py <1STMG|TSTMG>")
    classe = CLASSES[cle]
    csv_path = RACINE / f"codes_prives_{cle}.csv"
    if not csv_path.exists():
        sys.exit(f"❌ {csv_path} introuvable : lance d'abord generate_codes.py pour la {cle}.")
    lignes = lire_codes(csv_path)

    doc = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>Tickets codes — {html.escape(classe["nom"])}</title>
<style>
  @page {{ size: A4 portrait; margin: 7mm 8mm; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: #fff; color: #1a1a1a;
    font-family: "Segoe UI", Inter, Arial, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  :root {{ --accent: {classe["accent"]}; }}

  /* ── Planche de tickets : 4 × 8 par page A4 ── */
  table.grille {{ border-collapse: collapse; table-layout: fixed; width: 100%; page-break-after: always; }}
  table.grille:last-of-type {{ page-break-after: auto; }}
  td.t {{ width: 25%; height: 35mm; padding: 0; vertical-align: top;
    border: 0.3mm dashed #9a9a9a; }}
  td.t.vide {{ border-color: transparent; }}
  .bar {{ height: 2mm; background: var(--accent); }}
  table.int {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
  table.int td {{ border: 0; padding: 0; vertical-align: top; }}
  td.txt {{ padding: 1.4mm 1mm 1mm 2.2mm; height: 32mm; }}
  td.qrbox {{ width: 17mm; padding: 1.6mm 1.2mm 0 0; text-align: center; }}
  .classe {{ font-size: 6.5pt; color: #555; letter-spacing: 0.02em; }}
  .nom {{ font-size: 9pt; font-weight: 700; margin-top: 1mm; line-height: 1.1; overflow: hidden; }}
  .prenom {{ font-size: 8.5pt; line-height: 1.1; overflow: hidden; }}
  .code {{ font-family: Consolas, "Courier New", monospace; font-size: 17pt; font-weight: 700;
    letter-spacing: 0.12em; margin: 1.6mm 0 0.8mm; color: #111; }}
  .aide {{ font-size: 5.6pt; color: #666; line-height: 1.25; margin-top: 1.2mm; }}
  .qr path {{ fill: #111; }}
  .url {{ font-size: 4.9pt; color: #555; line-height: 1.15; margin-top: 0.6mm; font-family: Consolas, monospace; }}

  /* ── Liste de contrôle (page suivante) ── */
  .controle {{ page-break-before: always; }}
  h1 {{ font-size: 14pt; margin: 0 0 2mm; border-left: 3mm solid var(--accent); padding-left: 3mm; }}
  .rappel {{ font-size: 8.5pt; color: #444; margin: 0 0 4mm; }}
  table.liste {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
  table.liste th, table.liste td {{ border: 0.25mm solid #bbb; padding: 1.1mm 2mm; text-align: left; }}
  table.liste th {{ background: #f0f0f0; font-weight: 600; }}
  table.liste td.mono {{ font-family: Consolas, "Courier New", monospace; font-weight: 700; letter-spacing: 0.08em; }}
  table.liste td.case {{ width: 12mm; }}
  table.liste th:nth-child(5), table.liste th:nth-child(6) {{ width: 12mm; text-align: center; }}
</style></head><body>
{page_tickets(lignes, classe)}
{page_controle(lignes, classe)}
</body></html>"""

    sortie = RACINE / f"tickets_codes_{cle}.html"
    sortie.write_text(doc, encoding="utf-8")
    return sortie, len(lignes)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage : python scripts/tickets_codes.py <1STMG|TSTMG>")
    sortie, nb = generer(sys.argv[1].upper())
    print(f"✅ {nb} tickets → {sortie}  (PRIVÉ, ne pas commit)")
    print("   Ouvre le fichier dans Chrome/Edge → Ctrl+P → A4, « Graphiques d'arrière-plan » coché → PDF ou imprimante.")
