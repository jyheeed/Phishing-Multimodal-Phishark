# PhiShark2026 — détection multimodale du phishing

Projet de classification binaire de scans web (phishing/bénin) à partir de plusieurs modalités :

- caractéristiques de l’URL et des métadonnées ;
- données techniques extraites des archives ;
- contenu HTML ;
- captures d’écran ;
- fusion tardive des modèles.

## Contenu du dépôt

- `Phishing Multimodale PhiShark2026.ipynb` : pipeline CRISP-DM complet, préparation, entraînement et évaluation ;
- `phishark2026_dashboard.html` : dashboard de présentation des statistiques et résultats ;
- `rapport_avancement_phishark2026.pdf` : rapport d’avancement ;
- `requirements.txt` : dépendances Python.

## Données

Les archives du dataset ne sont pas versionnées dans Git : elles représentent plusieurs dizaines de gigaoctets. Placez le dossier `phisharkl2026dataset-v1.1` à la racine du projet, avec notamment :

```text
phisharkl2026dataset-v1.1/
├── phishark2026_public_metadata.csv
├── schemas/
└── *.zip
```

Le notebook vérifie la présence des données et utilise désormais ce chemin relatif au projet.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Pour une installation CPU de PyTorch, utiliser si nécessaire :

```powershell
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Exécution

Depuis la racine du dépôt :

```powershell
jupyter notebook
```

Exécutez les cellules dans l’ordre. L’extraction des archives et l’entraînement des CNN peuvent prendre plusieurs minutes. Les résultats de fusion sont exportés automatiquement vers `results/late_fusion_results.csv`.
