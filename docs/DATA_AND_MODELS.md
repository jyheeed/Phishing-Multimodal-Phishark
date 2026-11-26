# Données, entraînement et provenance

## Données originales

Le corpus original PhiShark2026 v1.1 reste local et n'est pas inclus dans Git. Il contient les archives de capture et `phishark2026_public_metadata.csv`. Obtenir le corpus auprès de sa source et respecter ses conditions de diffusion ; aucune licence du dataset n'est ajoutée par ce dépôt.

Sur Windows, depuis la racine du projet :

```powershell
.\scripts\connect_dataset.ps1 -Dataset 'C:\chemin\vers\phisharkl2026dataset-v1.1'
```

Ce script crée `data/raw` comme jonction vers le corpus existant, sans le dupliquer. Il refuse d'écraser une destination existante. Sur Linux/macOS, placer le corpus dans `data/raw` ou créer un lien symbolique équivalent. `data/processed` et `data/splits` sont générés par le notebook FULL et exclus de Git.

## Notebook autonome

`notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb` contient tout le pipeline scientifique : extraction, regroupement des entités/contenus, partitions, prétraitement, entraînements, fusions, combinaisons, calibration, métriques, bootstrap et analyse. Aucun module d'entraînement externe n'est nécessaire.

- `PRESENTATION` : lecture des résultats agrégés publiés, sans corpus original ni chargement des réseaux.
- `FULL_EXPERIMENT` : nouvelle expérience complète ; installer `requirements_full.txt`, connecter le corpus, modifier le mode, enregistrer puis redémarrer le noyau et tout exécuter. Le temps et la mémoire nécessaires dépendent du matériel. Aucun ancien résultat n'est attribué à ce nouveau code.

VS Code fournit l'identité du fichier via `__vsc_ipynb_file__`. Pour un autre client Jupyter, renseigner `NOTEBOOK_PATH` dans la première cellule avec le chemin réel, enregistrer puis redémarrer. Pour un lanceur automatique, fournir `PHISHARK_NOTEBOOK_FILE`. Le contrôle empêche de mélanger du code en mémoire et une autre version enregistrée.

## Modèles livrés

`models/` contient les poids réels U1–U4 et M2, la politique M1, les 11 têtes logistiques des combinaisons, les prétraitements et seuils gelés. Les 22 combinaisons correspondent à 11 sous-ensembles de modalités et deux méthodes de fusion. Ce ne sont pas 22 CNN supplémentaires.

`models/manifest.json` vérifie les fichiers nécessaires à l'inférence. Les fichiers `frozen.json` gardent la provenance originale ; certaines références historiques concernent des caches privés d'entraînement non distribués. L'inférence utilise uniquement les fichiers explicitement livrés et vérifiés par le manifeste de déploiement. Ne jamais charger des checkpoints ou fichiers joblib provenant d'une source non fiable.

`artifacts/provenance/executed_full_code.json` conserve le code exact producteur des poids : c'est une trace de provenance, pas un deuxième notebook à exécuter. Les fonctions d'inférence du notebook courant sont comparées à cette provenance par empreintes AST. Python 3.12 est requis pour garder cette représentation identique à l'environnement validé.

## Résultats partageables et données privées

`artifacts/published/manifest.json` garantit les empreintes des résultats agrégés. La démonstration conserve les scores et labels réels, avec un identifiant anonymisé. Les ZIP, URL par scan, embeddings, journaux de prédictions et états privés de recherche restent hors de Git.

Les checkpoints, partitions et métriques de l'expérience FULL locale ont été conservés dans `artifacts/runs`, `data/splits` et le cache actif. Les anciennes générations du projet sont dans `.local_archive`, également ignoré. Leur absence dans un clone neuf n'empêche ni la présentation ni l'analyse d'une URL ou d'un ZIP importé.
