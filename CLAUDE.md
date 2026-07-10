# Mes Copies — Pilotage complet des corrections

Ce dossier est le repo de l'application « Mes Copies » (GitHub Pages) ET l'espace de
travail des corrections. Tu peux être sollicité pour mener une correction de A à Z :
corriger les copies d'un devoir, puis publier les résultats dans les données de l'app.

## Structure

```
mes-copies/
├── index.html, app/, manifest.json, sw.js, icons/   ← l'application (publiée)
├── data/                                            ← données de l'app (publiées)
│   ├── devoirs.json
│   └── eleves/<code>.json
├── scripts/                                         ← outils de l'app
│   ├── generate_codes.py
│   └── update_app_data.py
├── codes_prives_1STMG.csv / codes_prives_TSTMG.csv  ← PRIVÉS (jamais publiés)
└── corrections/                                     ← PRIVÉ (jamais publié)
    └── <un sous-dossier par devoir>/
        ├── CLAUDE.md        ← le workflow détaillé de correction : LIS-LE ET SUIS-LE
        ├── bareme.json, devoir.json, sujet/, corrige/, copies/, ...
        └── sortie/resultats_app.json   ← produit en fin de correction
```

## Règle de confidentialité ABSOLUE

Le dossier `corrections/` et les fichiers `codes_prives_*.csv` contiennent des noms
d'élèves. Ils ne doivent JAMAIS être poussés sur GitHub ni copiés dans `data/`
(le `.gitignore` les exclut). Les seules données publiées sont anonymisées par
`update_app_data.py` (codes à 6 caractères).

## Workflow complet d'un devoir

1. **Corriger** : va dans le sous-dossier du devoir dans `corrections/`, lis son
   `CLAUDE.md` et exécute intégralement son workflow (transcriptions → corrections →
   PDF → recap → `sortie/resultats_app.json`).

2. **Publier dans les données de l'app** (depuis la racine du repo) :
   ```bash
   python scripts/update_app_data.py corrections/<devoir>/sortie/resultats_app.json --codes codes_prives_<CLASSE>.csv
   ```
   Le script anonymise, calcule moyenne/percentiles et met à jour `data/`.
   Si un élève est introuvable dans le CSV des codes, il s'arrête en le nommant :
   corrige l'orthographe du nom dans le JSON de correction concerné et relance.

3. **Mettre en ligne (automatique)** :
   ```bash
   git add data/
   git status --short        # CONTRÔLE : uniquement des fichiers data/ doivent apparaître
   git commit -m "<titre du devoir>"
   git push
   ```
   - Vérifie IMPÉRATIVEMENT avec `git status` que seuls des fichiers de `data/` (et
     éventuellement l'app si elle a été modifiée) partent. Si un fichier de `corrections/`
     ou un CSV apparaît, ARRÊTE-TOI : le `.gitignore` est cassé, répare-le d'abord.
   - Confirme au professeur que c'est en ligne (le déploiement GitHub Pages prend 2-3 min).
   - Si git n'est pas installé ou le dossier pas encore relié au repo, propose d'abord
     la procédure « Première connexion git » ci-dessous ; en dernier recours seulement,
     affiche la liste des fichiers de `data/` à uploader à la main sur GitHub.

### Première connexion git (une seule fois)
Si le dossier n'est pas encore un dépôt git relié au repo GitHub du professeur :
1. Vérifie que git est installé (`git --version`) ; sinon installe-le (`winget install Git.Git`
   sous Windows) et configure `git config --global user.name` / `user.email`.
2. ⚠️ AVANT tout : vérifie avec le professeur que le `data/` local est bien à jour par
   rapport à ce qui est en ligne (c'est le local qui va faire foi et écraser le distant).
3. `git init` → `git branch -M main` → `git remote add origin <URL du repo>` →
   `git add -A` (le `.gitignore` exclut automatiquement corrections/ et les CSV — vérifie
   avec `git status` qu'aucun nom d'élève ne part) → `git commit -m "Migration git"` →
   `git push --force-with-lease origin main`.
4. Au premier push, une fenêtre de connexion GitHub s'ouvre dans le navigateur
   (Git Credential Manager) : le professeur se connecte une fois, c'est mémorisé.

4. **Débloquer la fiche de synthèse** (généralement demandé le jour du ramassage,
   sans attendre la correction) : dans `data/devoirs.json`, bloc `chapitres`, passer
   `fiche_visible` à `true` pour le chapitre concerné (et renseigner `fiche` avec
   l'URL Objectif BAC si ce n'est pas déjà fait). C'est le professeur qui décide du
   moment ; ne jamais le faire sans son accord explicite.

5. **Vérification finale** : rappelle au professeur de tester avec un code élève du CSV.

## Pour créer le dossier d'un nouveau devoir

Duplique le dossier de devoir le plus récent de `corrections/`, puis, à partir du nouveau
sujet et du corrigé fournis par le professeur : régénère `bareme.json` (mêmes conventions : chaque question porte `capacite` (id du référentiel data/capacites.json) et `transversales` ;
checklists chiffrées dont la somme vaut exactement la note_max de chaque question, total 20,
variantes de notation) et `devoir.json` (nouvel `id` unique, `type` dossier/lecon/bac, `coef` fixé par le professeur, `chapitre` existant ou à créer dans le bloc chapitres, bon `theme` parmi ceux de
`data/devoirs.json`, date du devoir). Vide `copies/`, `transcriptions/`, `corrections/`,
`sortie/`. Les scripts sont réutilisables tels quels.
