#!/usr/bin/env python3
"""
Génère les codes personnels anonymes des élèves.

Usage :
    python generate_codes.py liste_eleves.csv 1STMG
    python generate_codes.py liste_eleves.csv TSTMG

Entrée : un CSV avec les colonnes  nom,prenom  (une ligne par élève).

Sorties :
    1. codes_prives_<CLASSE>.csv  → la correspondance nom/prénom ↔ code.
       ⚠️ FICHIER PRIVÉ : à garder sur ton ordinateur, JAMAIS dans le repo
       (il est couvert par le .gitignore fourni).
    2. ../data/eleves/<code>.json → un squelette vide par élève,
       que l'app peut déjà charger (écran « aucune copie »).

Le code est dérivé d'un hachage nom+prénom+SEL : stable dans le temps
(relancer le script redonne les mêmes codes) et impossible à deviner
sans connaître le sel.
"""

import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
import sys; sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── SEL SECRET (hors du script) ─────────────────────────────────────────
# Le sel n'est PLUS écrit en dur ici : il est lu depuis « sel_prive.txt », à la
# racine de mes-copies (une seule ligne). Ce fichier est PRIVÉ (couvert par le
# .gitignore) et ne doit JAMAIS être publié. N'en change plus la valeur une fois
# fixée, sinon tous les codes déjà distribués changeraient.
RACINE = Path(__file__).resolve().parent.parent
SEL_FICHIER = RACINE / "sel_prive.txt"
SEL = None  # chargé au lancement depuis sel_prive.txt


def charger_sel() -> str:
    if not SEL_FICHIER.exists():
        sys.exit(
            f"❌ Fichier de sel introuvable : {SEL_FICHIER}\n"
            "   Crée un fichier « sel_prive.txt » à la racine de mes-copies, contenant\n"
            "   sur une SEULE ligne ta phrase secrète (le SEL). Ne le publie jamais\n"
            "   (il est exclu par le .gitignore) et n'en change plus la valeur, sinon\n"
            "   tous les codes déjà distribués changeraient."
        )
    sel = SEL_FICHIER.read_text(encoding="utf-8").strip()
    if not sel:
        sys.exit(f"❌ Le fichier {SEL_FICHIER} est vide : mets-y ta phrase secrète (le SEL) sur une ligne.")
    return sel


# ────────────────────────────────────────────────────────────────────────

ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"  # sans 0/O, 1/l/i : lisible au tableau


def make_code(nom: str, prenom: str, classe: str) -> str:
    h = hashlib.sha256(f"{nom.strip().lower()}|{prenom.strip().lower()}|{classe}|{SEL}".encode()).digest()
    n = int.from_bytes(h[:8], "big")
    code = ""
    for _ in range(6):
        code += ALPHABET[n % len(ALPHABET)]
        n //= len(ALPHABET)
    return code


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage : python generate_codes.py liste_eleves.csv <1STMG|TSTMG>")

    csv_path = Path(sys.argv[1])
    classe = sys.argv[2].upper()
    if classe not in ("1STMG", "TSTMG"):
        sys.exit("La classe doit être 1STMG ou TSTMG.")
    global SEL
    SEL = charger_sel()

    eleves_dir = Path(__file__).resolve().parent.parent / "data" / "eleves"
    eleves_dir.mkdir(parents=True, exist_ok=True)

    lignes = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        # Excel FR enregistre souvent en ';' — on détecte automatiquement
        extrait = f.read(2048)
        f.seek(0)
        delim = ";" if extrait.count(";") > extrait.count(",") else ","
        lecteur = csv.DictReader(f, delimiter=delim)
        # En-têtes normalisés : "Nom ", "PRENOM", "prénom"... tout est accepté
        lecteur.fieldnames = [
            (c or "").strip().lower().replace("é", "e").replace("è", "e")
            for c in (lecteur.fieldnames or [])
        ]
        if "nom" not in lecteur.fieldnames or "prenom" not in lecteur.fieldnames:
            sys.exit(
                f"❌ Colonnes trouvées : {lecteur.fieldnames}\n"
                "   Le CSV doit contenir les colonnes 'nom' et 'prenom' en première ligne."
            )
        for row in lecteur:
            nom, prenom = (row["nom"] or "").strip(), (row["prenom"] or "").strip()
            if not nom and not prenom:
                continue  # ligne vide en fin de fichier Excel
            code = make_code(nom, prenom, classe)
            lignes.append((nom, prenom, code))

            fichier = eleves_dir / f"{code}.json"
            if not fichier.exists():
                fichier.write_text(
                    json.dumps(
                        {"code": code, "classe": classe, "maj": date.today().isoformat(), "copies": []},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )

    doublons = len(lignes) - len({c for *_, c in lignes})
    if doublons:
        sys.exit("⚠️  Collision de codes détectée (très rare) : change légèrement le SEL et relance.")

    sortie = Path(f"codes_prives_{classe}.csv")
    with open(sortie, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nom", "prenom", "code"])
        w.writerows(sorted(lignes))

    print(f"✅ {len(lignes)} codes générés pour la {classe}.")
    print(f"   → Correspondance privée : {sortie}  (NE PAS COMMIT)")
    print(f"   → Squelettes créés dans : {eleves_dir}")
    print("   Distribue à chaque élève son code (petit papier individuel ou Pronote en MP).")


if __name__ == "__main__":
    main()
