# PhiShark2026 — détection multimodale du phishing

Projet académique CRISP-DM : URL, HTML, screenshot et caractéristiques techniques ; quatre modèles unimodaux, deux fusions principales et 22 combinaisons sur encodeurs gelés.

Le notebook scientifique complet est **[PhiShark2026_FINAL_CRISP_DM.ipynb](notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb)** : 225 cellules, dont 122 de code. C'est l'unique notebook actif. L'interface utilise ses définitions d'inférence vérifiées et les checkpoints réels fournis.

## Démarrage

Python **3.12**, dans un environnement isolé, depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ouvrir **http://127.0.0.1:8502**. Le lanceur `LANCER_INTERFACE.ps1` utilise le Python de l'environnement actif. Sur Linux/macOS, activer `.venv/bin/activate`.

- **URL seule** : inférence du CNN URL U1, sans visiter le site.
- **Capture ZIP** : branches disponibles, fusions M1/M2 et, en option, 22 combinaisons.
- **Résultats** : tableaux vérifiés des expériences historiques.
- **Exemples locaux** : disponibles si le corpus et les artefacts privés sont installés ; facultatifs pour les autres fonctions.

Les scores sont des sorties du prototype, pas une garantie de sécurité ni une probabilité de risque externe validée.

## Notebook et reproduction

Ouvrir le notebook, sélectionner le noyau Python 3.12, puis **Tout exécuter**. Le mode par défaut `PRESENTATION` lit les preuves publiées, sans données originales, sans charger les réseaux et sans entraînement. Dans VS Code, le chemin réel du fichier est détecté ; avec un autre client, renseigner `NOTEBOOK_PATH` ou `PHISHARK_NOTEBOOK_FILE` comme expliqué dans le [guide de reproduction](docs/DATA_AND_MODELS.md).

Pour une **nouvelle expérience FULL**, installer `requirements_full.txt`, connecter le corpus original à `data/raw`, passer à `MODE = 'FULL_EXPERIMENT'`, enregistrer, redémarrer le noyau et exécuter dans l'ordre. Le code et les résultats antérieurs restent distincts : une modification du notebook crée une nouvelle signature et peut demander de nouveaux calculs. Le FULL n'a pas été relancé lors du nettoyage.

## Organisation

```text
notebooks/                 Un seul notebook scientifique autonome
src/app_inference.py       Adaptateur d'inférence vérifié pour l'interface
app.py                     Interface Streamlit locale
models/                    Poids, prétraitements et seuils gelés + manifeste
artifacts/published/       Résultats agrégés vérifiés et démonstration anonymisée
artifacts/provenance/      Source exacte ayant produit les poids existants
artifacts/interface/       Empreintes des définitions d'inférence
artifacts/verification/    Preuves compactes de vérification
data/                      Corpus, caches et partitions locaux, hors Git
docs/                      Reproduction, sujet et nettoyage
reports/                   Rapport final, analyses et figures
presentation/              Soutenance, script oral et questions du jury
scripts/                   Publication, contrôle et restitution des résultats
tests/                     Invariants scientifiques et tests de l'interface
```

Les anciennes générations sont archivées localement dans `.local_archive/`, exclu de Git. Les données originales, environnements, caches, partitions et sorties privées ne sont pas publiés. Les modèles compacts et les résultats agrégés nécessaires à la démonstration sont inclus. Voir [données et provenance](docs/DATA_AND_MODELS.md).

## Validation

```powershell
python -m pip install -r requirements_dev.txt
python -m pytest -q
python scripts/check_repository.py
python scripts/verify_presentation.py
```

Le test de parité sur une capture réelle est facultatif et ignoré si le corpus privé est absent. Le vérificateur de présentation écrit sa copie exécutée dans les artefacts locaux ; le notebook livré conserve des sorties vides pour des différences Git lisibles. Les versions de l'environnement validé sont enregistrées dans `requirements_validated.txt` ; scikit-learn est fixé pour les têtes sérialisées.

## Résultats et limites

Les 28 configurations sont comparées sur **13 212 scans communs**, soit 98,31 % du test complet de 13 439 scans. Les comparaisons internes sont exploratoires : aucun gagnant final indépendant n'est sélectionné sur ce test déjà examiné. Les 22 combinaisons représentent 11 sous-ensembles × deux méthodes, et non 22 nouveaux CNN.

La validation temporelle RQ2 reste non démontrée : après purge, la calibration correspondante ne contient aucun bénin. Spark reste `BLOCKED_RESOURCE` dans l'expérience enregistrée ; les 24 mesures pandas sont réelles. Aucun score temporel ni temps Spark n'est inventé. La généralisation externe demande un nouveau lot indépendant.

- [Rapport final](reports/PHISHARK2026_RAPPORT_FINAL.md) · [PDF](reports/PHISHARK2026_RAPPORT_FINAL.pdf)
- [Cadrage scientifique](reports/scientific/01_REVUE_CRITIQUE_LITTERATURE.md) · [Hypothèses et preuves](reports/scientific/02_HYPOTHESES_ET_PREUVES.md) · [Vérification scientifique](reports/VERIFICATION_SCIENTIFIQUE.md)
- [Argumentaire de soutenance](presentation/ARGUMENTAIRE_SOUTENANCE.md) · [Bibliographie](reports/BIBLIOGRAPHIE.bib) · [Tables et figures sources](reports/FIGURES_ET_RESULTATS/)
- [Soutenance](presentation/PHISHARK2026_SOUTENANCE.pptx)
- [Script oral](presentation/SCRIPT_ORAL.md) · [Questions du jury](presentation/QUESTIONS_JURY.md)
- [Guide de test de l'interface](reports/TESTER_INTERFACE.md)
- [Bilan du nettoyage](docs/CLEANUP_REPORT.md)
