#!/usr/bin/env python3
"""
Moteur de publication v3.
Intègre les résultats d'un devoir puis recalcule, pour toute la classe :
  - rang et moyenne de classe sur chaque copie
  - moyennes et classements PONDÉRÉS PAR LES COEFFICIENTS :
      général · par type d'évaluation (dossier/lecon/bac) · par matière · par thème
  - le cumul de points par capacité (thématiques et transversales) de chaque élève

Usage :
    python update_app_data.py resultats_devoir.json [--codes codes_prives_TSTMG.csv]

Le devoir doit porter : id, classe, matiere, theme, chapitre, type, coef, titre, date.
Chaque retour de question peut porter : capacite (id), transversales (liste d'ids),
reponse_attendue — ils sont republiés tels quels vers l'app.
Relancer sur un devoir déjà publié le met à jour et recalcule tout.
"""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # accents lisibles dans le terminal Windows

RACINE = Path(__file__).resolve().parent.parent
DEVOIRS_JSON = RACINE / "data" / "devoirs.json"
CAPACITES_JSON = RACINE / "data" / "capacites.json"
ELEVES_DIR = RACINE / "data" / "eleves"

TYPES_VALIDES = {"dossier", "lecon", "bac"}


def charger(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def sauver(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def charger_mapping(csv_path: Path) -> dict:
    mapping = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            mapping[(row["nom"].strip().lower(), row["prenom"].strip().lower())] = row["code"].strip()
    return mapping


def rang_de(valeur: float, valeurs: list) -> int:
    return 1 + sum(1 for v in valeurs if v > valeur + 1e-9)


def sur20(note: float, note_max: float) -> float:
    return note * 20 / note_max if note_max else note


# ── Recalcul complet d'une classe ────────────────────────────────────────

def recalculer_classe(conf: dict, classe: str) -> None:
    devoirs = {d["id"]: d for d in conf["devoirs"] if d["classe"] == classe}
    eleves = []
    for f in sorted(ELEVES_DIR.glob("*.json")):
        e = charger(f)
        if e.get("classe") == classe:
            eleves.append((f, e))

    # 1) Rang et stats par devoir
    for did, d in devoirs.items():
        parts = [(e, c) for _, e in eleves for c in e.get("copies", []) if c["devoir_id"] == did]
        if not parts:
            d.pop("stats", None)
            continue
        notes = [c["note"] for _, c in parts]
        d["stats"] = {"moyenne": round(sum(notes) / len(notes), 1), "effectif": len(notes)}
        for _, c in parts:
            c["rang"] = rang_de(c["note"], notes)
            c["effectif"] = len(notes)
            c["moyenne_classe"] = d["stats"]["moyenne"]

    # 2) Moyennes pondérées par périmètre
    def moyennes(filtre) -> dict:
        m = {}
        for _, e in eleves:
            num = den = 0.0
            for c in e.get("copies", []):
                d = devoirs.get(c["devoir_id"])
                if d and filtre(d):
                    coef = float(d.get("coef", 1))
                    num += sur20(c["note"], d.get("note_max", 20)) * coef
                    den += coef
            if den:
                m[e["code"]] = round(num / den, 2)
        return m

    perimetres = {"general": moyennes(lambda d: True)}
    for typ in TYPES_VALIDES:
        perimetres[f"type:{typ}"] = moyennes(lambda d, t=typ: d.get("type") == t)
    for mat in ("droit", "eco"):
        perimetres[f"matiere:{mat}"] = moyennes(lambda d, m=mat: d["matiere"] == m)
    themes = {d["theme"] for d in devoirs.values()}
    for th in themes:
        perimetres[f"theme:{th}"] = moyennes(lambda d, t=th: d["theme"] == t)

    # 3) Écriture par élève : classements + capacités
    for f, e in eleves:
        ancien = (e.get("classements", {}).get("general") or {}).get("rang")

        def bloc(cle):
            m = perimetres.get(cle, {})
            if e["code"] not in m:
                return None
            return {"rang": rang_de(m[e["code"]], list(m.values())), "effectif": len(m), "moyenne": m[e["code"]]}

        cl = {"general": bloc("general")}
        if cl["general"] and ancien and ancien != cl["general"]["rang"]:
            cl["general"]["rang_precedent"] = ancien
        cl["types"] = {t: b for t in ("dossier", "lecon", "bac") if (b := bloc(f"type:{t}"))}
        cl["matieres"] = {m: b for m in ("droit", "eco") if (b := bloc(f"matiere:{m}"))}
        cl["themes"] = {t: b for t in sorted(themes) if (b := bloc(f"theme:{t}"))}
        e["classements"] = cl

        # Cumul de points par capacité (thématiques + transversales)
        caps = {}
        for c in e.get("copies", []):
            if c["devoir_id"] not in devoirs:
                continue
            for r in c.get("retours", []):
                pmax = float(r.get("points_max") or 0)
                if not pmax:
                    continue
                pts = float(r.get("points") or 0)
                cibles = []
                if r.get("capacite"):
                    cibles.append(r["capacite"])
                cibles += r.get("transversales") or []
                for cid in cibles:
                    caps.setdefault(cid, {"pts": 0.0, "max": 0.0})
                    caps[cid]["pts"] = round(caps[cid]["pts"] + pts, 2)
                    caps[cid]["max"] = round(caps[cid]["max"] + pmax, 2)
        e["capacites"] = caps
        e["maj"] = date.today().isoformat()
        sauver(f, e)


# ── Programme principal ──────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("resultats")
    ap.add_argument("--codes")
    args = ap.parse_args()

    resultats = charger(Path(args.resultats))
    devoir = resultats["devoir"]
    lignes = resultats["resultats"]
    mapping = charger_mapping(Path(args.codes)) if args.codes else {}

    conf = charger(DEVOIRS_JSON)
    devoir.setdefault("note_max", 20)
    devoir.setdefault("coef", 1)
    if devoir.get("type") not in TYPES_VALIDES:
        sys.exit(f"❌ Le devoir doit avoir un type parmi {sorted(TYPES_VALIDES)} (reçu : {devoir.get('type')!r})")

    # Vérifications de cohérence (thème, chapitre, capacités)
    themes_valides = {t["id"] for mat in conf["programme"].get(devoir["classe"], {}).values() for t in mat}
    if devoir.get("theme") not in themes_valides:
        print(f"⚠️  Thème « {devoir.get('theme')} » inconnu pour la {devoir['classe']}")
    chapitres = {c["id"] for c in conf.get("chapitres", {}).get(devoir["classe"], [])}
    if devoir.get("chapitre") and devoir["chapitre"] not in chapitres:
        print(f"⚠️  Chapitre « {devoir['chapitre']} » absent de devoirs.json → ajoute-le au bloc chapitres")
    ref = charger(CAPACITES_JSON)
    ids_caps = {c["id"] for c in ref["transversales"]}
    for niv in ref["thematiques"].values():
        for mat in niv.values():
            for t in mat.values():
                ids_caps |= {c["id"] for c in t["capacites"]}
    inconnues = {
        cid
        for r in lignes
        for q in r.get("retours", [])
        for cid in ([q.get("capacite")] if q.get("capacite") else []) + (q.get("transversales") or [])
        if cid not in ids_caps
    }
    if inconnues:
        sys.exit(f"❌ Capacités inconnues du référentiel : {sorted(inconnues)}")

    # Upsert du devoir
    existants = [d for d in conf["devoirs"] if d["id"] == devoir["id"]]
    if existants:
        existants[0].update(devoir)
        print(f"↻ Devoir « {devoir['titre']} » mis à jour (type {devoir['type']}, coef {devoir['coef']})")
    else:
        conf["devoirs"].append(devoir)
        print(f"＋ Devoir « {devoir['titre']} » ajouté (type {devoir['type']}, coef {devoir['coef']})")

    # Résolution des codes
    for r in lignes:
        if "code" not in r:
            cle = (r["nom"].strip().lower(), r["prenom"].strip().lower())
            if cle not in mapping:
                sys.exit(f"❌ Élève introuvable dans le CSV des codes : {r['nom']} {r['prenom']}")
            r["code"] = mapping[cle]

    # Fusion des copies
    aujourd_hui = date.today().isoformat()
    for r in lignes:
        fichier = ELEVES_DIR / f"{r['code']}.json"
        eleve = charger(fichier) if fichier.exists() else {"code": r["code"], "classe": devoir["classe"], "copies": []}
        anciennes = {c["devoir_id"]: c for c in eleve["copies"]}
        copie = {
            "devoir_id": devoir["id"],
            "note": float(r["note"]),
            "publie_le": anciennes.get(devoir["id"], {}).get("publie_le", aujourd_hui),
            "pdf": r.get("pdf"),
            "retours": r.get("retours", []),
        }
        eleve["copies"] = [c for c in eleve["copies"] if c["devoir_id"] != devoir["id"]] + [copie]
        sauver(fichier, eleve)

    recalculer_classe(conf, devoir["classe"])
    sauver(DEVOIRS_JSON, conf)

    notes = [float(r["note"]) for r in lignes]
    print(f"\n✅ {len(lignes)} copies intégrées · moyenne {round(sum(notes)/len(notes), 1)}/{devoir['note_max']}")
    print("   Classements (général/types/matières/thèmes) et capacités recalculés.")
    print("   Publie : upload data/eleves/*.json puis data/devoirs.json sur GitHub (ou git push).")


if __name__ == "__main__":
    main()
