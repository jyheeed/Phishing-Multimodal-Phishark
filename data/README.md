# Données locales

- `raw/` : corpus original uniquement, connecté avec `scripts/connect_dataset.ps1`.
- `processed/` : extraction et caches générés par le notebook FULL.
- `splits/` : partitions versionnées par signature du pipeline, générées localement.

Ces trois répertoires sont exclus de Git. Ils restent présents sur la machine de travail. Un clone neuf utilise les modèles de `models/` et les résultats agrégés de `artifacts/published/` pour la présentation et l'interface ; le corpus n'est nécessaire que pour une nouvelle expérience FULL ou les exemples historiques locaux.

Voir [la procédure de reproduction](../docs/DATA_AND_MODELS.md).
