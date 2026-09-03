# Mes Copies — Éco-Droit STMG

PWA de restitution des copies corrigées pour la **Première STMG** et la **Terminale STMG** en Économie-Droit. v3 : types d'évaluation (dossier / contrôle de leçon / type bac) avec **coefficient libre par devoir**, moyennes et classements pondérés (général, par type, par matière, par thème, avec évolution), **suivi par capacités** (référentiel officiel du BO dans `data/capacites.json`, 7 transversales + 139 thématiques), **réponse attendue** affichée dans chaque retour, **fiches de synthèse par chapitre** débloquées manuellement pour toute la classe (`chapitres[].fiche_visible` dans devoirs.json), priorités de révision raisonnées en capacités, et **tableau de bord professeur** (`/prof/`) à 5 vues — le CSV des codes y est chargé localement et ne quitte jamais l'appareil.

**Tester** : ouvre l'app avec un code élève pris dans `codes_prives_<CLASSE>.csv` (les codes de démo ont été retirés avant la mise en production).

---

## 1. Mise en ligne (une seule fois)

1. Crée un repo GitHub **public** (ex. `mes-copies`) et pousse tout le contenu de ce dossier.
2. Sur GitHub : *Settings → Pages → Source : Deploy from a branch → main → / (root)*.
3. L'app est en ligne sur `https://<ton-user>.github.io/mes-copies/`.
4. Sur téléphone, les élèves ouvrent l'URL puis **« Ajouter à l'écran d'accueil »** : l'app s'installe comme une application native (icône, plein écran, hors-ligne).

## 2. Générer les codes élèves (une fois par classe)

1. Prépare un CSV par classe, `liste_eleves_1STMG.csv` / `liste_eleves_TSTMG.csv`, avec les colonnes `nom,prenom`.
2. Crée à la racine un fichier `sel_prive.txt` contenant sur une seule ligne ta phrase secrète (le SEL, à ne plus jamais changer). Il est exclu de Git ; sans lui le script refuse de tourner.
3. Lance :
   ```bash
   python scripts/generate_codes.py liste_eleves_1STMG.csv 1STMG
   python scripts/generate_codes.py liste_eleves_TSTMG.csv TSTMG
   ```
4. Tu obtiens `codes_prives_1STMG.csv` / `codes_prives_TSTMG.csv` : la correspondance nom ↔ code. **Ces fichiers restent sur ton ordinateur** (le `.gitignore` les bloque).
5. Pour distribuer les codes, génère une planche de tickets à découper (page 2 = liste de contrôle) :
   ```bash
   python scripts/tickets_codes.py 1STMG
   ```
   Ouvre `tickets_codes_1STMG.html` dans Chrome/Edge, Ctrl+P, « Enregistrer au format PDF ». Fichier privé, exclu de Git.

## 3. Publier un devoir corrigé (le workflow régulier)

1. Ton pipeline Claude Code corrige les copies comme d'habitude (barème JSON, checklists).
2. En fin de correction, le dossier du devoir contient `sortie/resultats_app.json` au format de `scripts/exemple_resultats.json` : le devoir porte `id, classe, matiere, theme, chapitre, type, coef, titre, date`, et les `retours` par question sont directement dérivés de la checklist du barème (tutoiement, pas d'appréciation générale).
3. Intègre puis publie :
   ```bash
   python scripts/update_app_data.py corrections/<devoir>/sortie/resultats_app.json --codes codes_prives_TSTMG.csv
   git add data/ && git commit -m "Devoir n°3 TSTMG" && git push
   ```
   Le script ajoute le devoir à `devoirs.json`, calcule moyenne et percentiles, et met à jour chaque `data/eleves/<code>.json`. Deux minutes après le push, les élèves voient leur copie.
4. *(Optionnel)* Dépose les PDF annotés dans un dossier `pdfs/` du repo et renseigne le champ `pdf` de chaque élève dans les résultats.

## 4. RGPD — règles intégrées au projet

- **Aucun nom dans le repo public** : uniquement des codes à 6 caractères non devinables (hachage salé). Le prénom affiché dans l'app est saisi par l'élève et reste dans le `localStorage` de son téléphone.
- **Pas de classement nominatif** : l'app affiche la moyenne de classe et « X % d'élèves derrière toi », jamais un rang ni les notes des autres.
- Les fichiers de correspondance sont exclus de Git par le `.gitignore`.
- Recommandé : informer les familles (mot carnet/Pronote) et déclarer le traitement au DPO académique.

## 5. Personnalisation

- **Thèmes du programme** : modifiables dans `data/devoirs.json` (`programme`), les identifiants `d1..d8` / `e1..e9` servent de référence dans les devoirs.
- **Couleurs** : accent par classe dans `devoirs.json` (`classes.*.accent`).
- **Badges** : la liste et les règles sont dans `app/index.html` (tableau `BADGES`), tout est calculé côté élève.
- Après modification de `index.html`/`app/index.html`, incrémente `VERSION` dans `sw.js` pour forcer la mise à jour chez les élèves.

## Workflow avec Claude Code (recommandé)

Ce dossier contient aussi `corrections/` (un sous-dossier par devoir) et un `CLAUDE.md`
racine. Pour corriger et publier un devoir : dépose les scans dans
`corrections/<devoir>/copies/`, ouvre Claude Code à la racine et demande-lui de corriger
le devoir et publier les résultats. Il termine par le `git push` des données. Le dossier
`corrections/` et les CSV de codes restent privés (exclus par le `.gitignore`).

## Lier les fiches de révision « Objectif BAC »

Dans `data/devoirs.json`, chaque thème du programme a un champ `lien` (par défaut `null`).
Renseigne-le avec l'URL de la fiche correspondante de ton site Objectif BAC : l'onglet
« Réviser » de l'app affichera alors un bouton direct vers la fiche des thèmes à retravailler.

## Structure

Publié sur GitHub Pages :
```
index.html            Écran de connexion par code
app/index.html        Application élève (copies, progression, capacités, badges)
prof/index.html       Tableau de bord professeur (charge le CSV des codes en local)
manifest.json, sw.js  Installation PWA + hors-ligne (incrémenter VERSION après modif de l'app)
icons/                Icônes de l'app
data/devoirs.json     Classes, programmes, chapitres, liste des devoirs
data/capacites.json   Référentiel officiel des capacités
data/eleves/*.json    Un fichier par élève (anonyme)
scripts/              generate_codes.py, tickets_codes.py, update_app_data.py, exemple_resultats.json
```

Privé, jamais publié (`.gitignore`) :
```
corrections/<devoir>/   Un dossier par devoir : CLAUDE.md, bareme.json, devoir.json, copies/, sortie/…
                        Nommé par l'id du chapitre (d5c1, d7c1, e6c1…) ; dupliquer le plus récent pour un nouveau devoir
chapitres/<id>/         Générateurs docx/pdf des livrets et cahiers de cours
liste_eleves_*.csv      Listes nominatives d'entrée
codes_prives_*.csv      Correspondance nom ↔ code
sel_prive.txt           Phrase secrète du hachage
tickets_codes_*.html    Planches de tickets à découper
```
